from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "role")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }

from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from .models import PasswordResetOTP
from django.core import signing
import random

RESET_TOKEN_SALT = "password-reset-signed"
RESET_TOKEN_TTL = 10 * 60  

class RequestResetSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        email = attrs.get("email", "").strip().lower()
        if not username and not email:
            raise serializers.ValidationError("Provide username or email")
        User = get_user_model()
        user = None
        if username:
            user = User.objects.filter(username=username).first()
        if not user and email:
            user = User.objects.filter(email=email).first()
        if not user and username and "@" in username:
            user = User.objects.filter(email=username.lower()).first()    
        if not user:
            raise serializers.ValidationError("User not found")
        attrs["user"] = user
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()

class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
