from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model

User = get_user_model()

class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.ADMIN  
        )
