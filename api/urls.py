# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnrollmentViewSet,
    # note: Subjects + assessments are provided via explicit paths below
    AssessmentsEolList, AssessmentsEolDetail,
    AssessmentsFaList, AssessmentsFaDetail,
    AssessmentsSaList, AssessmentsSaDetail,
    SubjectsList, SubjectsDetail,
    health, AssessmentWeightsViewSet, UsersTableViewSet, MypGradeBoundariesViewSet,
    LmsUsersUserViewSet, LmsUsersStaffpreapprovedViewSet, TokenBlacklistOutstandingtokenViewSet,
    TokenBlacklistBlacklistedtokenViewSet, DpGradeBoundariesViewSet
)

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
# keep other router registrations for ORM-backed viewsets
router.register(r"assessment-weights", AssessmentWeightsViewSet, basename="assessment-weights")
router.register(r"users-table", UsersTableViewSet, basename="users-table")
router.register(r"myp-grade-boundaries", MypGradeBoundariesViewSet, basename="myp-grade-boundaries")
router.register(r"lms-users", LmsUsersUserViewSet, basename="lms-users")
router.register(r"lms-users-preapproved", LmsUsersStaffpreapprovedViewSet, basename="lms-users-preapproved")
router.register(r"token-outstanding", TokenBlacklistOutstandingtokenViewSet, basename="token-outstanding")
router.register(r"token-blacklisted", TokenBlacklistBlacklistedtokenViewSet, basename="token-blacklisted")
router.register(r"dp-grade-boundaries", DpGradeBoundariesViewSet, basename="dp-grade-boundaries")

urlpatterns = [
    path("", include(router.urls)),
    path("health/", health, name="api-health"),

    # Subjects (raw SQL)
    path("subjects/", SubjectsList.as_view(), name="subjects-list"),
    path("subjects/<path:pk>/", SubjectsDetail.as_view(), name="subjects-detail"),

    # EOL (raw SQL)
    path("assessments/eol/", AssessmentsEolList.as_view(), name="assessments-eol-list"),
    path("assessments/eol/<path:pk>/", AssessmentsEolDetail.as_view(), name="assessments-eol-detail"),

    # FA (raw SQL)
    path("assessments/fa/", AssessmentsFaList.as_view(), name="assessments-fa-list"),
    path("assessments/fa/<path:pk>/", AssessmentsFaDetail.as_view(), name="assessments-fa-detail"),

    # SA (raw SQL)
    path("assessments/sa/", AssessmentsSaList.as_view(), name="assessments-sa-list"),
    path("assessments/sa/<path:pk>/", AssessmentsSaDetail.as_view(), name="assessments-sa-detail"),
]

# ensure router viewsets accept arbitrary chars for lookup value
for r in router.registry:
    viewset = r[1]
    viewset.lookup_value_regex = ".+"
