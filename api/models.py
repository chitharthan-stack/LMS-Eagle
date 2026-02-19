# merged_models.py
# Merged from your models.py and tmp_models_autogen.py (Neon DB inspected)
# Source: user models.py and tmp autogen. Keep managed=False unless you will run migrations.
from django.db import models

# --- LMS users / auth-like tables (reflects DB)
class LmsUsersPasswordresetotp(models.Model):
    id = models.AutoField(primary_key=True)
    otp = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    used = models.TextField(blank=True, null=True)
    user_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "LMS_users_passwordresetotp"


class LmsUsersStaffpreapproved(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True)
    invite_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    used = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "LMS_users_staffpreapproved"


class LmsUsersUser(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.TextField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    is_staff = models.TextField(blank=True, null=True)
    is_active = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "LMS_users_user"

# --- Token blacklist tables (if you use simplejwt/token_blacklist)
class TokenBlacklistBlacklistedtoken(models.Model):
    id = models.AutoField(primary_key=True)
    blacklisted_at = models.DateTimeField(blank=True, null=True)
    token_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "token_blacklist_blacklistedtoken"


class TokenBlacklistOutstandingtoken(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    user_id = models.TextField(blank=True, null=True)
    jti = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "token_blacklist_outstandingtoken"


# --- Core tables observed in Neon DB
class Enrollments(models.Model):
    user_email = models.TextField(blank=True, null=True)
    user_name = models.TextField(blank=True, null=True)
    academic_year = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    school = models.TextField(blank=True, null=True)
    enrollment_id = models.TextField(primary_key=True, db_column='enrollment_id')
    current_pct_overall = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predictive_pct_overall = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_overall = models.TextField(blank=True, null=True)
    prescriptive_overall = models.TextField(blank=True, null=True)
    engagement_analysis_overall = models.TextField(blank=True, null=True)
    engagement_analysis = models.JSONField(blank=True, null=True)
    strongest_subject = models.TextField(blank=True, null=True)
    weakest_subject = models.TextField(blank=True, null=True)
    subjects_taken = models.TextField(blank=True, null=True)
    current = models.TextField(blank=True, null=True)
    current_grade_overall = models.TextField(blank=True, null=True)
    predicted_grade_overall = models.TextField(blank=True, null=True)
    total_grade_overall = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "enrollments"



class Subjects(models.Model):
    enrollment_id = models.TextField(primary_key=True, db_column='enrollment_id')
    subject = models.TextField(blank=True, null=True)
    
    grade = models.TextField(blank=True, null=True)
    
    current_sub_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_sub_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    current_sub_ib = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    predicted_sub_ib = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    descriptive_sub = models.TextField(blank=True, null=True)
    prescriptive_sub = models.TextField(blank=True, null=True)
    engagement_analysis_sub = models.TextField(blank=True, null=True)
    current_sub = models.TextField(blank=True, null=True)
    dates = models.TextField(blank=True, null=True)
    engagement_analysis = models.JSONField(blank=True, null=True)
    
    current_sub_grade = models.TextField(blank=True, null=True)
    predicted_sub_grade = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "subjects"


class AssessmentsEol(models.Model):
    enrollment_id = models.TextField(primary_key=True, db_column='enrollment_id')
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    topic = models.TextField(blank=True, null=True)
    teachers = models.TextField(blank=True, null=True)
    obtained_marks = models.TextField(blank=True, null=True)
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cnt = models.TextField(blank=True, null=True)
    average = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_eol"


class AssessmentsFa(models.Model):
    enrollment_id = models.TextField(primary_key=True, db_column='enrollment_id')
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    month = models.TextField(blank=True, null=True)
    evaluation_criteria = models.TextField(blank=True, null=True)
    task_name = models.TextField(blank=True, null=True)
    teachers = models.TextField(blank=True, null=True)
    student_score = models.TextField(blank=True, null=True)
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
    
    predicted_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_fa"


class AssessmentsSa(models.Model):
    enrollment_id = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    month = models.TextField(blank=True, null=True)
    evaluation_criteria = models.TextField(blank=True, null=True)
    task_name = models.TextField(blank=True, null=True)
    teachers = models.TextField(blank=True, null=True)
    student_score = models.TextField(blank=True, null=True)
    max_score_old = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
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
    current_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)
    
    previous_hye_t1_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t1_max = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t1_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t2_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t2_max = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    previous_hye_t2_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_sa"


class AssessmentWeights(models.Model):
    academic_year = models.TextField(primary_key=True, db_column='academic_year')
    grade = models.IntegerField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessment_weights"


class DpGradeBoundaries(models.Model):
    subject = models.TextField(primary_key=True, db_column='subject')
    level = models.TextField(blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)
    min_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dp_grade_boundaries"


class MypGradeBoundaries(models.Model):
    grade = models.IntegerField(blank=True, null=True)
    boundary_level = models.IntegerField(blank=True, null=True)
    min_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "myp_grade_boundaries"


class UsersTable(models.Model):
    email = models.TextField(primary_key=True, db_column='email')
    username = models.TextField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    confirm_password = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users_table"

class AssessmentsNonAcademic(models.Model):
    enrollment_id = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    task_name = models.TextField(blank=True, null=True)
    student_score = models.TextField(blank=True, null=True)
    max_score_old = models.TextField(blank=True, null=True)
    total_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_non_academic"
