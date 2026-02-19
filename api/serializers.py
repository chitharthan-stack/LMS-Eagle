from rest_framework import serializers
from . import models

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollments  # adjust to the exact class name generated
        fields = "__all__"

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subjects
        fields = "__all__"

class AssessmentEOLSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentsEol
        fields = "__all__"

class AssessmentFASerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentsFa
        fields = "__all__"

class AssessmentSASerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentsSa
        fields = "__all__"

# api/serializers.py (append)

class AssessmentWeightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentWeights
        fields = "__all__"


class UsersTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UsersTable
        fields = "__all__"

# api/serializers.py (append)

class MypGradeBoundariesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MypGradeBoundaries
        fields = "__all__"

class LmsUsersUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LmsUsersUser
        # hide password field from responses
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = fields

class LmsUsersStaffpreapprovedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LmsUsersStaffpreapproved
        fields = "__all__"
        # don't set read_only_fields to the string '__all__' — omit it or use a tuple/list
        # if you want everything read-only:
        read_only_fields = tuple(f.name for f in models.LmsUsersStaffpreapproved._meta.fields)


class TokenBlacklistOutstandingtokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TokenBlacklistOutstandingtoken
        fields = "__all__"
        read_only_fields = tuple(f.name for f in models.TokenBlacklistOutstandingtoken._meta.fields)


class TokenBlacklistBlacklistedtokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TokenBlacklistBlacklistedtoken
        fields = "__all__"
        read_only_fields = tuple(f.name for f in models.TokenBlacklistBlacklistedtoken._meta.fields)


class DpGradeBoundariesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DpGradeBoundaries
        fields = "__all__"
        read_only_fields = tuple(f.name for f in models.DpGradeBoundaries._meta.fields)


class AssessmentNonAcademicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentsNonAcademic
        fields = "__all__"
