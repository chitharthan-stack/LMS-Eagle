# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class LmsUsersPasswordresetotp(models.Model):
    id = models.UUIDField(primary_key=True)
    otp = models.CharField(max_length=8)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    used = models.BooleanField()
    user = models.ForeignKey('LmsUsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'LMS_users_passwordresetotp'


class LmsUsersStaffpreapproved(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=254)
    role = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    invite_token = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    used = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'LMS_users_staffpreapproved'


class LmsUsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    email = models.CharField(unique=True, max_length=254)
    role = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'LMS_users_user'


class LmsUsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(LmsUsersUser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'LMS_users_user_groups'
        unique_together = (('user', 'group'),)


class LmsUsersUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(LmsUsersUser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'LMS_users_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AssessmentWeights(models.Model):
    pk = models.CompositePrimaryKey('academic_year', 'grade', 'term', 'assessment_type')
    academic_year = models.TextField()
    grade = models.IntegerField()
    term = models.TextField()
    assessment_type = models.TextField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'assessment_weights'


class AssessmentsEol(models.Model):
    pk = models.CompositePrimaryKey('enrollment_id', 'subject')
    enrollment = models.ForeignKey('Enrollments', models.DO_NOTHING)
    subject = models.TextField()
    grade = models.TextField()
    assessment_type = models.TextField()
    topic = models.TextField(blank=True, null=True)  # This field type is a guess.
    teachers = models.TextField(blank=True, null=True)  # This field type is a guess.
    obtained_marks = models.TextField(blank=True, null=True)  # This field type is a guess.
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cnt = models.IntegerField(blank=True, null=True)
    average = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assessments_eol'


class AssessmentsFa(models.Model):
    pk = models.CompositePrimaryKey('enrollment_id', 'subject', 'evaluation_criteria')
    enrollment = models.ForeignKey('Enrollments', models.DO_NOTHING)
    subject = models.TextField()
    grade = models.TextField()
    assessment_type = models.TextField()
    month = models.TextField()  # This field type is a guess.
    evaluation_criteria = models.TextField()
    task_name = models.TextField(blank=True, null=True)  # This field type is a guess.
    teachers = models.TextField(blank=True, null=True)  # This field type is a guess.
    student_score = models.TextField(blank=True, null=True)  # This field type is a guess.
    max_score_old = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    count_sdl_t1 = models.IntegerField(blank=True, null=True)
    count_sdl_t2 = models.IntegerField(blank=True, null=True)
    count_sdl_t3 = models.IntegerField(blank=True, null=True)
    count_wt_t1 = models.IntegerField(blank=True, null=True)
    count_wt_t2 = models.IntegerField(blank=True, null=True)
    count_wt_t3 = models.IntegerField(blank=True, null=True)
    count_fawriting_t1 = models.IntegerField(blank=True, null=True)
    count_fawriting_t2 = models.IntegerField(blank=True, null=True)
    count_fawriting_t3 = models.IntegerField(blank=True, null=True)
    count_steam_t1 = models.IntegerField(blank=True, null=True)
    count_steam_t2 = models.IntegerField(blank=True, null=True)
    count_steam_t3 = models.IntegerField(blank=True, null=True)
    count_ia_t1 = models.IntegerField(blank=True, null=True)
    count_ia_t2 = models.IntegerField(blank=True, null=True)
    count_ia_t3 = models.IntegerField(blank=True, null=True)
    current_average_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    current_percentage_t1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    current_percentage_t2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    current_percentage_t3 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage_t3 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assessments_fa'


class AssessmentsSa(models.Model):
    pk = models.CompositePrimaryKey('enrollment_id', 'subject', 'evaluation_criteria')
    enrollment = models.ForeignKey('Enrollments', models.DO_NOTHING)
    subject = models.TextField()
    grade = models.TextField()
    assessment_type = models.TextField()
    month = models.TextField()  # This field type is a guess.
    evaluation_criteria = models.TextField()
    task_name = models.TextField(blank=True, null=True)  # This field type is a guess.
    teachers = models.TextField(blank=True, null=True)  # This field type is a guess.
    student_score = models.TextField(blank=True, null=True)  # This field type is a guess.
    max_score_old = models.TextField(blank=True, null=True)  # This field type is a guess.
    count_sa = models.IntegerField(blank=True, null=True)
    count_hye_t1 = models.IntegerField(blank=True, null=True)
    count_hye_t2 = models.IntegerField(blank=True, null=True)
    count_project_t1 = models.IntegerField(blank=True, null=True)
    count_project_t2 = models.IntegerField(blank=True, null=True)
    count_projects_t1 = models.IntegerField(blank=True, null=True)
    count_projects_t2 = models.IntegerField(blank=True, null=True)
    count_december_test = models.IntegerField(blank=True, null=True)
    count_mock = models.IntegerField(blank=True, null=True)
    count_others = models.IntegerField(blank=True, null=True)
    current_average_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)
    previous_hye_t1_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t1_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t1_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t2_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t2_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t2_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assessments_sa'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(LmsUsersUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DpGradeBoundaries(models.Model):
    pk = models.CompositePrimaryKey('subject', 'level', 'grade', 'min_score')
    subject = models.TextField()
    level = models.TextField()
    grade = models.IntegerField()
    min_score = models.DecimalField(max_digits=6, decimal_places=2)
    max_score = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'dp_grade_boundaries'


class Enrollments(models.Model):
    user_email = models.TextField()  # This field type is a guess.
    user_name = models.TextField()
    academic_year = models.TextField()
    grade = models.TextField()
    school = models.TextField(blank=True, null=True)
    enrollment_id = models.TextField(primary_key=True)
    current_pct_overall = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predictive_pct_overall = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    descriptive_overall = models.TextField(blank=True, null=True)
    prescriptive_overall = models.TextField(blank=True, null=True)
    engagement_analysis_overall = models.TextField(blank=True, null=True)
    engagement_analysis = models.JSONField(blank=True, null=True)
    strongest_subject = models.TextField(blank=True, null=True)
    weakest_subject = models.TextField(blank=True, null=True)
    subjects_taken = models.TextField(blank=True, null=True)  # This field type is a guess.
    current = models.TextField(blank=True, null=True)  # This field type is a guess.
    current_grade_overall = models.TextField(blank=True, null=True)
    predicted_grade_overall = models.TextField(blank=True, null=True)
    total_grade_overall = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enrollments'
        unique_together = (('user_email', 'academic_year'),)


class MypGradeBoundaries(models.Model):
    pk = models.CompositePrimaryKey('grade', 'boundary_level')
    grade = models.IntegerField()
    boundary_level = models.IntegerField()
    min_score = models.DecimalField(max_digits=6, decimal_places=2)
    max_score = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'myp_grade_boundaries'


class Subjects(models.Model):
    pk = models.CompositePrimaryKey('enrollment_id', 'subject')
    enrollment = models.ForeignKey(Enrollments, models.DO_NOTHING)
    subject = models.TextField()
    grade = models.TextField()
    current_sub_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_sub_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    current_sub_ib = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_sub_ib = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    descriptive_sub = models.TextField(blank=True, null=True)
    prescriptive_sub = models.TextField(blank=True, null=True)
    engagement_analysis_sub = models.TextField(blank=True, null=True)
    current_sub = models.TextField(blank=True, null=True)  # This field type is a guess.
    dates = models.TextField(blank=True, null=True)  # This field type is a guess.
    engagement_analysis = models.JSONField(blank=True, null=True)
    current_sub_grade = models.TextField(blank=True, null=True)
    predicted_sub_grade = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subjects'


class TokenBlacklistBlacklistedtoken(models.Model):
    id = models.BigAutoField(primary_key=True)
    blacklisted_at = models.DateTimeField()
    token = models.OneToOneField('TokenBlacklistOutstandingtoken', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'token_blacklist_blacklistedtoken'


class TokenBlacklistOutstandingtoken(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()
    user = models.ForeignKey(LmsUsersUser, models.DO_NOTHING, blank=True, null=True)
    jti = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'token_blacklist_outstandingtoken'


class UsersTable(models.Model):
    email = models.TextField(primary_key=True)  # This field type is a guess.
    username = models.TextField(unique=True)  # This field type is a guess.
    password = models.TextField()
    confirm_password = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_table'
