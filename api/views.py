# api/views.py
from urllib.parse import unquote
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ParseError
from .permissions import ReadOnlyOrAdmin
from . import models, serializers
from django.db import connection
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

# ------------------------------------------------------------
# Pagination + healthcheck (unchanged)
# ------------------------------------------------------------
class DefaultPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    with connection.cursor() as cur:
        cur.execute("SELECT 1;")
        row = cur.fetchone()
    return Response({"status": "ok", "db": bool(row and row[0] == 1)})

# ------------------------------------------------------------
# Composite lookup mixin (keeps behaviour for viewsets that use ORM)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Helper for raw-SQL read-only viewsets (to avoid 'id' expectation)
# ------------------------------------------------------------
def dictfetchall(cursor):
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

class RawReadOnlyViewSet(viewsets.ViewSet):
    """
    Generic read-only ViewSet using raw SQL to avoid Django expecting 'id' PK.
    Subclasses must set `table_name` and implement parse_pk_parts(parts) -> (where_sql, params).
    Provides:
      - list(self, request)
      - retrieve(self, request, pk)
    """
    permission_classes = [ReadOnlyOrAdmin]
    table_name: str = None
    safety_limit = 1000
    # ensure router accepts arbitrary lookup values (keeps parity with other viewsets)
    lookup_value_regex = ".+"

    def list(self, request):
        if not self.table_name:
            return Response({"detail": "table_name not configured"}, status=500)

        q = request.query_params.get("q")
        sql = f"SELECT * FROM {self.table_name}"
        params = []

        if q:
            # permissive text search; no guarantee that columns exist on every table but this is graceful.
            sql += " WHERE (CAST(enrollment_id AS TEXT) ILIKE %s OR CAST(subject AS TEXT) ILIKE %s)"
            params = [f"%{q}%", f"%{q}%"]

        sql += f" LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql, params)
            rows = dictfetchall(cur)
        return Response(rows)

    def retrieve(self, request, pk=None):
        if not self.table_name:
            return Response({"detail": "table_name not configured"}, status=500)
        if pk is None:
            return Response({"detail": "No id provided"}, status=400)

        # decode parts separated by "~"
        parts = [unquote(p) for p in pk.split("~")]

        # ---- Special case: single-part pk -> treat as enrollment_id list request ----
        if len(parts) == 1:
            # if subclass defines list_by_enrollment, call it (returns multiple rows)
            enrollment_id = parts[0]
            if hasattr(self, "list_by_enrollment"):
                return self.list_by_enrollment(request, enrollment_id=enrollment_id)

            # fallback: run simple WHERE on enrollment_id and return first row (existing semantics)
            where_sql = "enrollment_id = %s"
            params = [enrollment_id]
            sql = f"SELECT * FROM {self.table_name} WHERE {where_sql} LIMIT 1"
            with connection.cursor() as cur:
                cur.execute(sql, params)
                rows = dictfetchall(cur)
            if not rows:
                return Response({"detail": "Not found"}, status=404)
            return Response(rows)

        # ---- 3-part or other (expected composite) ----
        try:
            where_sql, params = self.parse_pk_parts(parts)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        # If parse_pk_parts returns a WHERE that can select multiple rows but the
        # intent was returning a single record we keep old LIMIT 1 behavior.
        sql = f"SELECT * FROM {self.table_name} WHERE {where_sql} LIMIT 1"
        with connection.cursor() as cur:
            cur.execute(sql, params)
            rows = dictfetchall(cur)
        if not rows:
            return Response({"detail": "Not found"}, status=404)
        return Response(rows)


# ------------------------------------------------------------
# Enrollment (unchanged; uses ORM and has enrollment_id lookup)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Subjects: use RawReadOnlyViewSet to avoid missing 'id' DB errors
# URL preserved: /api/subjects/
# Key format for retrieve: <enrollment_id>~<subject>
# ------------------------------------------------------------
class SubjectViewSet(RawReadOnlyViewSet):
    table_name = "subjects"
    def parse_pk_parts(self, parts):
        if len(parts) != 2:
            raise ValueError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return "enrollment_id = %s AND subject = %s", [enrollment_id, subject]

# ------------------------------------------------------------
# Assessments EOL (read-only via raw SQL)
# URL preserved: /api/assessments/eol/
# Key format for retrieve: <enrollment_id>~<subject>
# ------------------------------------------------------------
class AssessmentEOLViewSet(RawReadOnlyViewSet):
    table_name = "assessments_eol"
    def parse_pk_parts(self, parts):
        if len(parts) != 2:
            raise ValueError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return "enrollment_id = %s AND subject = %s", [enrollment_id, subject]

# ------------------------------------------------------------
# Assessments FA (read-only via raw SQL)
# URL preserved: /api/assessments/fa/
# Key format for retrieve: <enrollment_id>~<subject>~<evaluation_criteria>
# Also provide a non-conflicting enrollment list path at 'enrollment/<enrollment_id>/'
# ------------------------------------------------------------
class AssessmentFAViewSet(RawReadOnlyViewSet):
    table_name = "assessments_fa"

    def parse_pk_parts(self, parts):
        if len(parts) != 3:
            raise ValueError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return (
            "enrollment_id = %s AND subject = %s AND evaluation_criteria = %s",
            [enrollment_id, subject, evaluation_criteria],
        )

    def _group_fa_rows(self, rows):
        grouped = {}

        for row in rows:
            key = (
                row["enrollment_id"],
                row["subject"],
                row["evaluation_criteria"],
            )

            if key not in grouped:
                grouped[key] = {
                    **{k: v for k, v in row.items()
                       if k not in ("month", "task_name", "teachers",
                                    "student_score", "max_score_old")},
                    "month": [],
                    "task_name": [],
                    "teachers": [],
                    "student_score": [],
                    "max_score_old": [],
                }

            grouped[key]["month"].extend(row["month"])
            grouped[key]["task_name"].extend(row["task_name"])
            grouped[key]["teachers"].extend(row["teachers"])

            grouped[key]["student_score"].extend([
                float(x) if x not in (None, "") else None
                for x in row["student_score"]
            ])

            grouped[key]["max_score_old"].extend([
                float(x) if x not in (None, "") else None
                for x in row["max_score_old"]
            ])

        # ---- DEDUPLICATE & SORT (CLEAN OUTPUT) ----
        cleaned = []
        for obj in grouped.values():

            combined = list(zip(
                obj["month"],
                obj["task_name"],
                obj["teachers"],
                obj["student_score"],
                obj["max_score_old"],
            ))

            # Remove duplicates but keep order
            unique = list(dict.fromkeys(combined))

            # Sort tasks by date (month field)
            unique.sort(key=lambda x: x[0])

            # Unzip back
            obj["month"] = [u[0] for u in unique]
            obj["task_name"] = [u[1] for u in unique]
            obj["teachers"] = [u[2] for u in unique]
            obj["student_score"] = [u[3] for u in unique]
            obj["max_score_old"] = [u[4] for u in unique]

            cleaned.append(obj)

        return cleaned

    def list(self, request):
        sql = f"SELECT * FROM {self.table_name} LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql)
            rows = dictfetchall(cur)
        return Response(self._group_fa_rows(rows))

    def list_by_enrollment(self, request, enrollment_id=None):
        if not enrollment_id:
            return Response({"detail": "No enrollment_id provided"}, status=400)

        sql = f"""
            SELECT *
            FROM {self.table_name}
            WHERE enrollment_id = %s
            LIMIT {self.safety_limit}
        """

        with connection.cursor() as cur:
            cur.execute(sql, [enrollment_id])
            rows = dictfetchall(cur)

        return Response(self._group_fa_rows(rows))

# ------------------------------------------------------------
# Assessments SA (read-only via raw SQL)
# URL preserved: /api/assessments/sa/
# Key format for retrieve: <enrollment_id>~<subject>~<evaluation_criteria>
# ------------------------------------------------------------
class AssessmentSAViewSet(RawReadOnlyViewSet):
    table_name = "assessments_sa"

    def parse_pk_parts(self, parts):
        if len(parts) != 3:
            raise ValueError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return "enrollment_id = %s AND subject = %s AND evaluation_criteria = %s", [
            enrollment_id,
            subject,
            evaluation_criteria,
        ]

    # ✅ NEW: Allow fetching all SA rows for one enrollment_id
    def list_by_enrollment(self, request, enrollment_id=None):
        if not enrollment_id:
            return Response({"detail": "No enrollment_id provided"}, status=400)
        sql = f"SELECT * FROM {self.table_name} WHERE enrollment_id = %s LIMIT {self.safety_limit}"
        with connection.cursor() as cur:
            cur.execute(sql, [enrollment_id])
            rows = dictfetchall(cur)
        return Response(rows)

# ------------------------------------------------------------
# AssessmentWeights (unchanged ORM usage)
# composite primary lookup by academic_year~grade~term~assessment_type
# ------------------------------------------------------------
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
        # grade is TextField in DB — do not coerce to int unless DB changes
        return {
            "academic_year": academic_year,
            "grade": grade,
            "term": term,
            "assessment_type": assessment_type,
        }

# ------------------------------------------------------------
# UsersTable + MypGradeBoundaries (Myp handled via raw SQL if table has no id)
# ------------------------------------------------------------
class UsersTableViewSet(viewsets.ModelViewSet):
    queryset = models.UsersTable.objects.all()
    serializer_class = serializers.UsersTableSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "username"]
    ordering_fields = "__all__"

# If myp_grade_boundaries has no 'id' column, use raw viewset; otherwise you can switch back to ModelViewSet.
class MypGradeBoundariesViewSet(RawReadOnlyViewSet):
    table_name = "myp_grade_boundaries"
    def parse_pk_parts(self, parts):
        if len(parts) != 2:
            raise ValueError("Expected '<grade>~<boundary_level>'")
        grade_str, boundary_level_str = parts
        return "grade = %s AND boundary_level = %s", [grade_str, boundary_level_str]

# ------------------------------------------------------------
# Lms users + token blacklist + dp grade boundaries (unchanged)
# ------------------------------------------------------------
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

class DpGradeBoundariesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.DpGradeBoundaries.objects.all()
    serializer_class = serializers.DpGradeBoundariesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'level', 'grade']
    filterset_fields = ['subject', 'level', 'grade']
