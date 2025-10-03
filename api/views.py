from urllib.parse import unquote
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ParseError
from .permissions import ReadOnlyOrAdmin
from . import models, serializers
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny ,IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

class DefaultPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200

# Healthcheck
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    with connection.cursor() as cur:
        cur.execute("SELECT 1;")
        row = cur.fetchone()
    return Response({"status": "ok", "db": bool(row and row[0] == 1)})


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


# Subjects (composite: enrollment_id~subject)
class SubjectViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    lookup_value_regex = ".+"
    # DO NOT use select_related('enrollment') — enrollment_id is a plain TextField in DB
    queryset = models.Subjects.objects.all()
    serializer_class = serializers.SubjectSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment_id', 'subject', 'grade']
    search_fields = ["enrollment_id", "subject"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 2:
            raise ParseError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return {"enrollment_id": enrollment_id, "subject": subject}


# EOL (composite: enrollment_id~subject)
class AssessmentEOLViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    lookup_value_regex = ".+"
    queryset = models.AssessmentsEol.objects.all()
    serializer_class = serializers.AssessmentEOLSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment_id', 'subject', 'grade', 'assessment_type']
    search_fields = ["enrollment_id", "subject", "assessment_type", "topic", "teachers"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 2:
            raise ParseError("Expected '<enrollment_id>~<subject>'")
        enrollment_id, subject = parts
        return {"enrollment_id": enrollment_id, "subject": subject}


# FA (composite: enrollment_id~subject~evaluation_criteria)
class AssessmentFAViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    lookup_value_regex = ".+"
    queryset = models.AssessmentsFa.objects.all()
    serializer_class = serializers.AssessmentFASerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment_id', 'subject', 'evaluation_criteria', 'assessment_type', 'month']
    search_fields = ["enrollment_id", "subject", "evaluation_criteria", "assessment_type", "month"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 3:
            raise ParseError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return {"enrollment_id": enrollment_id, "subject": subject, "evaluation_criteria": evaluation_criteria}

    # custom endpoint: GET /api/assessments/fa/{enrollment_id}/
    @action(detail=False, methods=["get"], url_path=r"(?P<enrollment_id>[^/]+)")
    def by_enrollment(self, request, enrollment_id=None):
        qs = self.get_queryset().filter(enrollment_id=enrollment_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# SA (composite: enrollment_id~subject~evaluation_criteria)
class AssessmentSAViewSet(CompositeLookupMixin, viewsets.ModelViewSet):
    lookup_value_regex = ".+"
    queryset = models.AssessmentsSa.objects.all()
    serializer_class = serializers.AssessmentSASerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment_id', 'subject', 'evaluation_criteria', 'assessment_type', 'month']
    search_fields = ["enrollment_id", "subject", "evaluation_criteria", "assessment_type", "month"]
    ordering_fields = "__all__"

    def parse_pk(self, pk: str) -> dict:
        parts = [unquote(p) for p in pk.split(self.pk_delim)]
        if len(parts) != 3:
            raise ParseError("Expected '<enrollment_id>~<subject>~<evaluation_criteria>'")
        enrollment_id, subject, evaluation_criteria = parts
        return {"enrollment_id": enrollment_id, "subject": subject, "evaluation_criteria": evaluation_criteria}

    # custom endpoint: GET /api/assessments/sa/{enrollment_id}/
    @action(detail=False, methods=["get"], url_path=r"(?P<enrollment_id>[^/]+)")
    def by_enrollment(self, request, enrollment_id=None):
        qs = self.get_queryset().filter(enrollment_id=enrollment_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# AssessmentWeights (composite: academic_year~grade~term~assessment_type)
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
        # grade & boundary_level are TextField in DB — keep as strings
        return {"grade": grade_str, "boundary_level": boundary_level_str}

# Lms users
class LmsUsersUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for LMS users table (existing DB table).
    """
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