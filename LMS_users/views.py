# LMS_USERS/views.py
from functools import wraps
import secrets

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect

from .models import StaffPreApproved

User = get_user_model()

def role_in(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("choose_login")
            if request.user.role == User.Roles.ADMIN:
                return view_func(request, *args, **kwargs)
            if request.user.role not in allowed_roles:
                messages.error(request, "You don't have permission to access this page")
                return redirect("choose_login")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# ---- One-time registration flow token ----
_FLOW_TTL_SECONDS = 10 * 60  # 10 minutes

def _issue_flow_token(request, role_upper: str) -> str:
    token = secrets.token_urlsafe(32)
    request.session["reg_flow"] = {
        "role": role_upper,
        "token": token,
        "ts": timezone.now().timestamp(),
    }
    request.session.modified = True
    return token

def _consume_flow_token(request, role_upper: str) -> bool:
    """Read token from Cookie (preferred) or header, verify against session + TTL, consume."""
    provided = request.COOKIES.get("reg_token") or request.headers.get("X-Reg-Token")
    data = request.session.get("reg_flow")
    if not provided or not data:
        return False
    if data.get("role") != role_upper or data.get("token") != provided:
        return False
    age = timezone.now().timestamp() - float(data.get("ts", 0))
    if age > _FLOW_TTL_SECONDS:
        return False
    request.session.pop("reg_flow", None)
    request.session.modified = True
    return True


@never_cache
@ensure_csrf_cookie
def choose_login(request):
    return render(request, "choose_login.html")


@never_cache
@ensure_csrf_cookie
def login_view(request, role):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            if user.role != role.upper() and user.role != User.Roles.ADMIN:
                messages.error(request, f"This account is not a {role.title()}")
                return redirect("login", role=role)
            login(request, user)
            if user.role == User.Roles.STUDENT:
                return redirect("student_dashboard")
            if user.role == User.Roles.STAFF:
                return redirect("staff_dashboard")
            if user.role == User.Roles.PARENT:
                return redirect("parent_dashboard")
            if user.role == User.Roles.ADMIN:
                return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "login.html", {"role": role.title()})


def logout_view(request):
    logout(request)
    return redirect("choose_login")


@never_cache
@ensure_csrf_cookie
@login_required
@role_in([User.Roles.STUDENT, User.Roles.STAFF])
def student_dashboard(request):
    return render(request, "student_dashboard.html")

@never_cache
@ensure_csrf_cookie
@login_required
@role_in([User.Roles.STAFF])
def staff_dashboard(request):
    return render(request, "staff_dashboard.html")

@never_cache
@ensure_csrf_cookie
@login_required
@role_in([User.Roles.PARENT])
def parent_dashboard(request):
    return render(request, "parent_dashboard.html")

@never_cache
@ensure_csrf_cookie
@login_required
@role_in([User.Roles.ADMIN])
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


@never_cache
@ensure_csrf_cookie
def register_view(request, role):
    role_upper = role.upper()

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm  = request.POST.get("confirm_password", "")

        if not email or not username or not password:
            messages.error(request, "All fields are required.")
            return redirect("register", role=role)
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register", role=role)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register", role=role)

        if role_upper in [User.Roles.STAFF, User.Roles.ADMIN]:
            if not StaffPreApproved.objects.filter(email__iexact=email).exists():
                messages.error(request, "This email is not recognized.")
                return redirect("register", role=role)
            if not _consume_flow_token(request, role_upper):
                messages.error(request, "Session expired. Please reload the page and try again.")
                return redirect("register", role=role)

        # Create user
        user = User(email=email, username=username, role=role_upper)
        user.set_password(password)
        if role_upper in [User.Roles.STAFF, User.Roles.ADMIN]:
            user.is_staff = True
        if role_upper == User.Roles.ADMIN:
            user.is_superuser = True
        user.save()

        messages.success(request, f"{role.title()} account created. Please log in.")
        resp: HttpResponseRedirect = redirect("login", role=role)
        resp.delete_cookie("reg_token")
        return resp

    ctx = {"role": role.title()}
    response: HttpResponse = render(request, "register.html", ctx)
    if role_upper in [User.Roles.STAFF, User.Roles.ADMIN]:
        token = _issue_flow_token(request, role_upper)
        response.set_cookie(
            "reg_token",
            token,
            max_age=_FLOW_TTL_SECONDS,
            httponly=True,    
            samesite="Lax",
            secure=False,
        )
    return response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core import signing
from datetime import timedelta

from .serializers import RequestResetSerializer, VerifyOTPSerializer, ResetPasswordSerializer
from .models import PasswordResetOTP
import random   

OTP_TTL_SECONDS = 10 * 60  
RESET_TOKEN_SALT = "password-reset-signed"   
RESET_TOKEN_TTL = 10 * 60 

def _generate_otp(n=6):
    range_start = 10**(n-1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))

class RequestPasswordResetView(APIView):
    permission_classes = ()  

    def post(self, request):
        s = RequestResetSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]

        otp = _generate_otp(6)
        expires = timezone.now() + timedelta(seconds=OTP_TTL_SECONDS)
        pr = PasswordResetOTP.objects.create(user=user, otp=otp, expires_at=expires)

        subject = "Your LMS password reset OTP"
        body = (
            f"Hello {user.username},\n\n"
            f"Use this OTP to reset your password: {otp}\n"
            f"This OTP expires in {OTP_TTL_SECONDS // 60} minutes.\n\n"
            "If you did not request this, ignore."
        )

        recipient = user.email if user.email else "sidhupkc@gmail.com"

        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        except Exception:
            pass

        return Response(
            {"detail": f"OTP sent (to {recipient}). For testing use the inbox of that address."},
            status=status.HTTP_200_OK,
        )
# Replace VerifyOTPView and ResetPasswordView in LMS_users/views.py with this code

class VerifyOTPView(APIView):
    permission_classes = ()

    def post(self, request):
        s = VerifyOTPSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data["username"].strip()  # may be username or email
        otp = s.validated_data["otp"]

        User = get_user_model()
        # try username then email then username-as-email
        user = User.objects.filter(username__iexact=identifier).first()
        if not user and "@" in identifier:
            user = User.objects.filter(email__iexact=identifier.lower()).first()

        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        pr = PasswordResetOTP.objects.filter(user=user, otp=otp, used=False).order_by("-created_at").first()
        if not pr or not pr.is_valid():
            return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # mark used
        pr.mark_used()

        # create signed reset token (short lived)
        payload = {"user_id": user.id, "otp_id": str(pr.id)}
        reset_token = signing.dumps(payload, salt=RESET_TOKEN_SALT)

        return Response({"reset_token": reset_token}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = ()

    def post(self, request):
        s = ResetPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data["username"].strip()
        reset_token = s.validated_data["reset_token"]
        new_password = s.validated_data["new_password"]

        User = get_user_model()
        user = User.objects.filter(username__iexact=identifier).first()
        if not user and "@" in identifier:
            user = User.objects.filter(email__iexact=identifier.lower()).first()

        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        # verify token
        try:
            payload = signing.loads(reset_token, salt=RESET_TOKEN_SALT, max_age=RESET_TOKEN_TTL)
        except signing.BadSignature:
            return Response({"detail": "Invalid reset token"}, status=status.HTTP_400_BAD_REQUEST)
        except signing.SignatureExpired:
            return Response({"detail": "Reset token expired"}, status=status.HTTP_400_BAD_REQUEST)

        if payload.get("user_id") != user.id:
            return Response({"detail": "Token does not match user"}, status=status.HTTP_400_BAD_REQUEST)

        otp_id = payload.get("otp_id")
        try:
            pr = PasswordResetOTP.objects.get(id=otp_id, user=user)
        except PasswordResetOTP.DoesNotExist:
            return Response({"detail": "OTP record missing"}, status=status.HTTP_400_BAD_REQUEST)

        if pr.used is not True:
            # extra safety: allow reset only if OTP was previously marked used at verify step
            return Response({"detail": "OTP not verified"}, status=status.HTTP_400_BAD_REQUEST)

        # all good: set password
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated"}, status=status.HTTP_200_OK)

#test