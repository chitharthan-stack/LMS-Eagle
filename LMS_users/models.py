# LMS_USERS/models.py
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core import signing


# -----------------------
# Custom User
# -----------------------
class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        STAFF   = "STAFF",   "Staff"
        PARENT  = "PARENT",  "Parent"
        ADMIN   = "ADMIN",   "Admin"

    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"


# -----------------------
# Invite token helpers (email-only)
# -----------------------
_INVITE_SALT = "staff-admin-invite"
_DEFAULT_TTL_SECONDS = 7 * 24 * 3600  # 7 days

def _make_token(email: str) -> str:
    """Create a signed token for this email (no role in payload)."""
    payload = {
        "email": email.strip().lower(),
        "ts": timezone.now().timestamp(),
    }
    return signing.dumps(payload, salt=_INVITE_SALT)

def _verify_token(token: str, max_age: int = _DEFAULT_TTL_SECONDS) -> dict:
    """Return payload on success; raises on bad/expired signatures."""
    return signing.loads(token, salt=_INVITE_SALT, max_age=max_age)


# -----------------------
# Pre-approved Staff/Admin
# -----------------------
class StaffPreApproved(models.Model):
    # NOTE: 'role' kept for admin display/reporting, but we don't validate against it.
    email = models.EmailField(unique=True)
    role  = models.CharField(
        max_length=10,
        choices=[(User.Roles.STAFF, "Staff"), (User.Roles.ADMIN, "Admin")],
        default=User.Roles.STAFF,
    )
    name       = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    # auto-generated invite (email-only token)
    invite_token = models.TextField(blank=True)
    expires_at   = models.DateTimeField(null=True, blank=True)
    used         = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # normalize email
        if self.email:
            self.email = self.email.strip().lower()

        # (re)generate token if missing/expired/used
        need_new = (
            not self.invite_token
            or not self.expires_at
            or self.expires_at <= timezone.now()
            or self.used
        )
        if need_new:
            self.invite_token = _make_token(self.email)  # email-only
            self.expires_at   = timezone.now() + timedelta(seconds=_DEFAULT_TTL_SECONDS)
            self.used         = False

        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        if self.used or not self.expires_at or self.expires_at <= timezone.now():
            return False
        try:
            data = _verify_token(self.invite_token)
            return data.get("email") == self.email
        except signing.BadSignature:
            return False

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"


# at bottom of LMS_users/models.py (append)
import uuid
from django.utils import timezone
from django.conf import settings

class PasswordResetOTP(models.Model):
    """
    Stores OTPs for password resets. One-time use; expires after TTL.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_otps")
    otp = models.CharField(max_length=8)               # store numeric / short string
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "otp"]),
        ]

    def is_valid(self):
        return (not self.used) and (self.expires_at and timezone.now() < self.expires_at)

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])
