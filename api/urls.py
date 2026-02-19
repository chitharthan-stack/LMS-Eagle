from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnrollmentViewSet, SubjectViewSet,
    AssessmentEOLViewSet, AssessmentFAViewSet, AssessmentSAViewSet,
    health, AssessmentWeightsViewSet, UsersTableViewSet, MypGradeBoundariesViewSet,
    LmsUsersUserViewSet, LmsUsersStaffpreapprovedViewSet, TokenBlacklistOutstandingtokenViewSet,
    TokenBlacklistBlacklistedtokenViewSet, DpGradeBoundariesViewSet,
    AssessmentNonAcademicViewSet,
)
from . import views


router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
router.register(r"subjects", SubjectViewSet, basename="subjects")
router.register(r"assessments/eol", AssessmentEOLViewSet, basename="assessments-eol")
router.register(r"assessments/fa",  AssessmentFAViewSet,  basename="assessments-fa")
router.register(r"assessments/sa",  AssessmentSAViewSet,  basename="assessments-sa")

# register other routes
router.register(r"assessment-weights", AssessmentWeightsViewSet, basename="assessment-weights")
router.register(r"users-table", UsersTableViewSet, basename="users-table")
router.register(r"myp-grade-boundaries", MypGradeBoundariesViewSet, basename="myp-grade-boundaries")
router.register(r"lms-users", LmsUsersUserViewSet, basename="lms-users")
router.register(r"lms-users-preapproved", LmsUsersStaffpreapprovedViewSet, basename="lms-users-preapproved")
router.register(r"token-outstanding", TokenBlacklistOutstandingtokenViewSet, basename="token-outstanding")
router.register(r"token-blacklisted", TokenBlacklistBlacklistedtokenViewSet, basename="token-blacklisted")
router.register(r"dp-grade-boundaries", DpGradeBoundariesViewSet, basename="dp-grade-boundaries")
router.register(r"assessments/non-academic", AssessmentNonAcademicViewSet, basename="assessments-non-academic")



urlpatterns = [
    path("", include(router.urls)),
    path("health/", health, name="api-health"),
    path(
    "assessments/fa/by-enrollment/<path:enrollment_id>/",
    views.AssessmentFAViewSet.as_view({"get": "list_by_enrollment"}),
    name="assessments-fa-by-enrollment",
    ),
    path(
        "assessments/sa/by-enrollment/<path:enrollment_id>/",
        views.AssessmentSAViewSet.as_view({"get": "list_by_enrollment"}),
        name="assessments-sa-by-enrollment",
    ),
    path(
    "assessments/non-academic/by-enrollment/<path:enrollment_id>/",
    views.AssessmentNonAcademicViewSet.as_view({"get": "list_by_enrollment"}),
    name="assessments-non-academic-by-enrollment",
    ),

]

# ensure router viewsets accept arbitrary chars for lookup value
for r in router.registry:
    viewset = r[1]
    viewset.lookup_value_regex = ".+"
