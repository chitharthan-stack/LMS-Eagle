# Auto-generated model suggestions. Review & merge into api/models.py
from django.db import models

class AssessmentWeights(models.Model):
    academic_year = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessment_weights"


class AssessmentsEol(models.Model):
    enrollment_id = models.TextField(blank=True, null=True)
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
    enrollment_id = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    assessment_type = models.TextField(blank=True, null=True)
    month = models.TextField(blank=True, null=True)
    evaluation_criteria = models.TextField(blank=True, null=True)
    task_name = models.TextField(blank=True, null=True)
    teachers = models.TextField(blank=True, null=True)
    student_score = models.TextField(blank=True, null=True)
    max_score_old = models.TextField(blank=True, null=True)
    count_sdl_t1 = models.TextField(blank=True, null=True)
    count_sdl_t2 = models.TextField(blank=True, null=True)
    count_sdl_t3 = models.TextField(blank=True, null=True)
    count_wt_t1 = models.TextField(blank=True, null=True)
    count_wt_t2 = models.TextField(blank=True, null=True)
    count_wt_t3 = models.TextField(blank=True, null=True)
    count_fawriting_t1 = models.TextField(blank=True, null=True)
    count_fawriting_t2 = models.TextField(blank=True, null=True)
    count_fawriting_t3 = models.TextField(blank=True, null=True)
    count_steam_t1 = models.TextField(blank=True, null=True)
    count_steam_t2 = models.TextField(blank=True, null=True)
    count_steam_t3 = models.TextField(blank=True, null=True)
    count_ia_t1 = models.TextField(blank=True, null=True)
    count_ia_t2 = models.TextField(blank=True, null=True)
    count_ia_t3 = models.TextField(blank=True, null=True)
    current_average_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_fa"


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
    max_score_old = models.TextField(blank=True, null=True)
    count_sa = models.TextField(blank=True, null=True)
    count_hye_t1 = models.TextField(blank=True, null=True)
    count_hye_t2 = models.TextField(blank=True, null=True)
    count_project_t1 = models.TextField(blank=True, null=True)
    count_project_t2 = models.TextField(blank=True, null=True)
    count_projects_t1 = models.TextField(blank=True, null=True)
    count_projects_t2 = models.TextField(blank=True, null=True)
    count_december_test = models.TextField(blank=True, null=True)
    count_mock = models.TextField(blank=True, null=True)
    count_others = models.TextField(blank=True, null=True)
    current_average_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_average_t3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_percentage_t2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriptive_analysis = models.TextField(blank=True, null=True)
    prescriptive_analysis = models.TextField(blank=True, null=True)
    previous_hye_t1_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t1_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t1_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t2_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t2_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_hye_t2_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "assessments_sa"


class Correlation(models.Model):
    enrollment_id = models.TextField(blank=True, null=True)
    eol_fa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_wt_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_le_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_phe_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_wt_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_le_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_phe_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_le_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_phe_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sdl_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sdl_le_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sdl_phe_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phe_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phe_le_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phe_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    le_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    le_wt_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    le_fa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    le_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    eol_fa_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_sdl_fa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phe_sdl_eol_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fa_le_sa_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_le_sdl_corr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    correlation_analysis = models.JSONField(blank=True, null=True)
    holistic_analysis = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "correlation"


class DpGradeBoundaries(models.Model):
    subject = models.TextField(blank=True, null=True)
    level = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    min_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dp_grade_boundaries"


class Enrollments(models.Model):
    user_email = models.TextField(blank=True, null=True)
    user_name = models.TextField(blank=True, null=True)
    academic_year = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    school = models.TextField(blank=True, null=True)
    enrollment_id = models.TextField(blank=True, null=True)
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


class MypGradeBoundaries(models.Model):
    grade = models.TextField(blank=True, null=True)
    boundary_level = models.TextField(blank=True, null=True)
    min_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "myp_grade_boundaries"


class Subjects(models.Model):
    enrollment_id = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)
    current_sub_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_sub_pct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_sub_ib = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_sub_ib = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
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


class UsersTable(models.Model):
    email = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    confirm_password = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users_table"


