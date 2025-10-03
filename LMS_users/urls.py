from django.urls import path
from .views import (
    choose_login, login_view, logout_view,
    student_dashboard, staff_dashboard, parent_dashboard, admin_dashboard,register_view,
    RequestPasswordResetView, VerifyOTPView, ResetPasswordView
)

urlpatterns = [
    # Role-based login entry
    path("", choose_login, name="choose_login"),
    path("login/<str:role>/", login_view, name="login"),
    
    path("logout/", logout_view, name="logout"),

    # Dashboards
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("staff/dashboard/",   staff_dashboard,   name="staff_dashboard"),
    path("parent/dashboard/",  parent_dashboard,  name="parent_dashboard"),
    path("admin/dashboard/",   admin_dashboard,   name="admin_dashboard"),

    path("register/<str:role>/", register_view, name="register"),

    path("api/auth/request-reset/", RequestPasswordResetView.as_view(), name="api_request_reset"),
    path("api/auth/verify-otp/", VerifyOTPView.as_view(), name="api_verify_otp"),
    path("api/auth/reset-password/", ResetPasswordView.as_view(), name="api_reset_password"),

]

