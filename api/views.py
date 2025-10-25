# api/views.py
from urllib.parse import unquote
from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ParseError
from .permissions import ReadOnlyOrAdmin
from . import models, serializers
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.views import APIView

# ---------- Pagination ----------
class DefaultPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200

# ---------- Healthcheck ----------
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    with connection.cursor() as cur:
        cur.execute("SELECT 1;")
        row = cur.fetchone()
    return Response({"status": "ok", "db": bool(row and row[0] == 1)})

# ---------- ORM-backed viewsets (unchanged) ----------
class CompositeLookupMixin:
    """
    Allow /{pk}/ by encoding composite keys with "~".
    Implement parse_pk() to return a dict filter for .get_queryset().filter(**filters).
    """
    pk_delim = "~"
    lookup_field = "pk"

    def parse_pk(self, pk: str) -> dict:
        raise NotImplementedError

    def get_object(self):
        pk = self.kwargs.get(self.lookup_field)
        if pk is None:
            raise NotFound("No id provided")
        try:
            filters = self.parse_pk(pk)
        except ParseError:
            raise
        except Exception:
            raise ParseError("Malformed id. Use '~' separated composite key.")
        obj = self.get_queryset().filter(**filters).first()
        if not obj:
            raise NotFound("Object not found")
        self.check_object_permissions(self.request, obj)
        return obj

# Enrollments (simple PK but lookup by enrollment_id)
class EnrollmentViewSet(viewsets.ModelViewSet):
    lookup_value_regex = ".+"
    queryset = models.Enrollments.objects.all()
    serializer_class = serializers.EnrollmentSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["enrollment_id", "user_email", "user_name", "academic_year", "grade", "school"]
    ordering_fields = "__all__"
    lookup_field = "enrollment_id"

# NOTE: Removed SubjectViewSet / AssessmentEOLViewSet / AssessmentFAViewSet / AssessmentSAViewSet
# from ModelViewSet usage — these are handled below with raw SQL read-only views.

# ---------- Raw SQL helpers & read-only views for problematic tables ----------
def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

class RawTableListView(APIView):
    """
    Generic read-only list view that selects * from a table.
    Subclass and set table_name.
    """
    permission_classes = [ReadOnlyOrAdmin]
    table_name = None
    safety_limit = 1000  # default limit for list endpoints

    def get(self, request, *args, **kwargs):
        if not self.table_name:
            return Response({"detail": "table_name not configured on view"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        q = request.query_params.get("q")
        params = []
        sql = f"SELECT * FROM {self.table_name}"
        # Very small & safe text-search implementation if `q` provided
        if q:
            sql += " WHERE (CAST(enrollment_id AS TEXT) ILIKE %s OR CAST(subject AS TEXT) ILIKE %s)"
            val = f"%{q}%"
            params.extend([val, val])
        sql += f" LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql, params)
            rows = dictfetchall(cur)
        return Response(rows)

class CompositeRowView(APIView):
    """
    Generic detail view for composite-key tables.
    Subclass, set table_name and implement parse_pk_parts(parts) -> (where_sql, params)
    """
    permission_classes = [ReadOnlyOrAdmin]
    table_name = None

    def parse_pk_parts(self, parts):
        raise NotImplementedError("subclass must implement parse_pk_parts")

    def get(self, request, pk=None, *args, **kwargs):
        if not self.table_name:
            return Response({"detail": "table_name not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if pk is None:
            return Response({"detail": "No id provided"}, status=status.HTTP_400_BAD_REQUEST)
        parts = [unquote(p) for p in pk.split("~")]
        try:
            where_sql, params = self.parse_pk_parts(parts)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        sql = f"SELECT * FROM {self.table_name} WHERE {where_sql} LIMIT 1"
        with connection.cursor() as cur:
            cur.execute(sql, params)
            rows = dictfetchall(cur)
        if not rows:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(rows[0])

# --- Subjects (list + detail)
class SubjectsList(RawTableListView):
    table_name = "subjects"

class SubjectsDetail(CompositeRowView):
    table_name = "subjects"
    def parse_pk_parts(self, parts):
        # expected format: enrollment_id~subject
        if len(parts) != 2:
            raise ValueError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return "enrollment_id = %s AND subject = %s", [enrollment_id, subject]

# --- EOL (list + detail: enrollment_id~subject)
class AssessmentsEolList(RawTableListView):
    table_name = "assessments_eol"

class AssessmentsEolDetail(CompositeRowView):
    table_name = "assessments_eol"
    def parse_pk_parts(self, parts):
        if len(parts) != 2:
            raise ValueError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return "enrollment_id = %s AND subject = %s", [enrollment_id, subject]

# --- FA (list + detail: enrollment_id~subject~evaluation_criteria)
class AssessmentsFaList(RawTableListView):
    table_name = "assessments_fa"

class AssessmentsFaDetail(CompositeRowView):
    table_name = "assessments_fa"
    def parse_pk_parts(self, parts):
        if len(parts) != 3:
            raise ValueError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return "enrollment_id = %s AND subject = %s AND evaluation_criteria = %s", [enrollment_id, subject, evaluation_criteria]

    # keep the same helper endpoint for listing by enrollment_id
    def get_queryset_by_enrollment(self, enrollment_id):
        sql = f"SELECT * FROM {self.table_name} WHERE enrollment_id = %s LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql, [enrollment_id])
            return dictfetchall(cur)

# --- SA (list + detail: enrollment_id~subject~evaluation_criteria)
class AssessmentsSaList(RawTableListView):
    table_name = "assessments_sa"

class AssessmentsSaDetail(CompositeRowView):
    table_name = "assessments_sa"
    def parse_pk_parts(self, parts):
        if len(parts) != 3:
            raise ValueError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return "enrollment_id = %s AND subject = %s AND evaluation_criteria = %s", [enrollment_id, subject, evaluation_criteria]

    # maintain the by_enrollment pattern from your previous viewset
    def list_by_enrollment(self, request, enrollment_id=None):
        sql = f"SELECT * FROM {self.table_name} WHERE enrollment_id = %s LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql, [enrollment_id])
            rows = dictfetchall(cur)
        return Response(rows)

# ---------- ORM-backed viewsets for everything else (unchanged) ----------

class AssessmentWeightsViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    """
    Detail id format:
      <academic_year>~<grade>~<term>~<assessment_type>
    """
    queryset = models.AssessmentWeights.objects.all()
    serializer_class = serializers.AssessmentWeightsSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["academic_year", "grade", "term", "assessment_type"]
    search_fields = ["academic_year", "grade", "term", "assessment_type"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 4:
            raise ParseError("Expected '<academic_year>~<grade>~<term>~<assessment_type>'")
        academic_year, grade, term, assessment_type = parts
        return {
            "academic_year": academic_year,
            "grade": grade,
            "term": term,
            "assessment_type": assessment_type,
        }

class UsersTableViewSet(viewsets.ModelViewSet):
    queryset = models.UsersTable.objects.all()
    serializer_class = serializers.UsersTableSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "username"]
    ordering_fields = "__all__"

class MypGradeBoundariesViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    """
    Detail id format:
      <grade>~<boundary_level>
    """
    lookup_value_regex = ".+"
    queryset = models.MypGradeBoundaries.objects.all()
    serializer_class = serializers.MypGradeBoundariesSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["grade", "boundary_level"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 2:
            raise ParseError("Expected '<grade>~<boundary_level>'")
        grade_str, boundary_level_str = parts
        return {"grade": grade_str, "boundary_level": boundary_level_str}

# Lms users
class LmsUsersUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.LmsUsersUser.objects.all()
    serializer_class = serializers.LmsUsersUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'role']
    filterset_fields = ['email', 'role']

class LmsUsersStaffpreapprovedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.LmsUsersStaffpreapproved.objects.all()
    serializer_class = serializers.LmsUsersStaffpreapprovedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'invite_token', 'name']
    filterset_fields = ['email', 'role']

# Token blacklist
class TokenBlacklistOutstandingtokenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TokenBlacklistOutstandingtoken.objects.all()
    serializer_class = serializers.TokenBlacklistOutstandingtokenSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_id', 'jti']
    filterset_fields = ['user_id']

class TokenBlacklistBlacklistedtokenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TokenBlacklistBlacklistedtoken.objects.all()
    serializer_class = serializers.TokenBlacklistBlacklistedtokenSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['token_id']
    filterset_fields = ['token_id']

# DP grade boundaries
class DpGradeBoundariesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.DpGradeBoundaries.objects.all()
    serializer_class = serializers.DpGradeBoundariesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'level', 'grade']
    filterset_fields = ['subject', 'level', 'grade']
