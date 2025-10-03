from django.contrib import admin
from . import models

@admin.register(models.Enrollments)
class EnrollmentsAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'user_email', 'user_name', 'academic_year', 'grade', 'school')
    search_fields = ('enrollment_id', 'user_email', 'user_name')
    list_filter = ('academic_year', 'grade', 'school')
    readonly_fields = [f.name for f in models.Enrollments._meta.fields]

@admin.register(models.Subjects)
class SubjectsAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'subject', 'grade', 'current_sub_pct')
    search_fields = ('enrollment_id', 'subject')
    readonly_fields = [f.name for f in models.Subjects._meta.fields]

@admin.register(models.AssessmentsEol)
class AssessmentsEolAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'subject', 'assessment_type', 'average')
    search_fields = ('enrollment_id', 'subject')

@admin.register(models.AssessmentsFa)
class AssessmentsFaAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'subject', 'assessment_type', 'current_percentage')
    search_fields = ('enrollment_id', 'subject')

@admin.register(models.AssessmentsSa)
class AssessmentsSaAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'subject', 'assessment_type', 'current_percentage')
    search_fields = ('enrollment_id', 'subject')

@admin.register(models.AssessmentWeights)
class AssessmentWeightsAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'grade', 'term', 'assessment_type', 'weight')
    search_fields = ('academic_year', 'grade', 'assessment_type')

@admin.register(models.UsersTable)
class UsersTableAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'created_at')
    search_fields = ('email', 'username')

@admin.register(models.LmsUsersUser)
class LmsUsersUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'username')

@admin.register(models.LmsUsersStaffpreapproved)
class LmsUsersStaffpreapprovedAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'name', 'department', 'invite_token', 'expires_at')
    search_fields = ('email', 'invite_token')

@admin.register(models.TokenBlacklistOutstandingtoken)
class TokenOutstandingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'created_at', 'expires_at')
    search_fields = ('user_id', 'jti')

@admin.register(models.TokenBlacklistBlacklistedtoken)
class TokenBlacklistedAdmin(admin.ModelAdmin):
    list_display = ('id', 'token_id', 'blacklisted_at')
    search_fields = ('token_id',)

@admin.register(models.DpGradeBoundaries)
class DpGradeBoundariesAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'grade', 'min_score', 'max_score')

@admin.register(models.MypGradeBoundaries)
class MypGradeBoundariesAdmin(admin.ModelAdmin):
    list_display = ('grade', 'boundary_level', 'min_score', 'max_score')
