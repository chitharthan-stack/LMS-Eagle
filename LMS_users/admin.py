from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User ,  StaffPreApproved

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username", "role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "role", "password1", "password2"),
        }),
    )
@admin.register(StaffPreApproved)
class StaffPreApprovedAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "department")
    search_fields = ("email", "name", "department")
    list_filter = ("department",)
    ordering = ("email",)