from django.db import models
from utils.utils import get_file_path
from student.models import UserStudentInfo
from tutor.models import TutorInfo


class CourseEdition(models.Model):

    ADVANCED = 1
    INTERNATIONAL = 2
    SG = 3

    edition_name = models.CharField(max_length=63)
    description = models.CharField(max_length=1023)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.edition_name

    class Meta:
        managed = False
        db_table = 'course_edition'


class CourseInfo(models.Model):
    course_edition = models.ForeignKey(CourseEdition, models.DO_NOTHING, related_name='course_info')
    course_name = models.CharField(max_length=63)
    course_level = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
         return '{}:{}'.format(self.course_name, self.course_edition.edition_name)

    class Meta:
        managed = False
        db_table = 'course_info'


class CourseExtcourseTag(models.Model):

    REQUIRED = 1
    OPTION = 2
    COURSE_TYPE_CHOICE = (
        (REQUIRED, 'Required'),
        (OPTION, 'Option')
    )

    tag = models.CharField(max_length=31, help_text='标签，Level1~Level6 古文 科普 写作')
    ext_course_type = models.IntegerField(choices=COURSE_TYPE_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_extcourse_tag'


class CourseLesson(models.Model):

    ACTIVE = 1
    ARCHIVED = 2

    STATUS_CHOICE = (
        (ACTIVE, 'ACTIVE'),
        (ARCHIVED, 'ARCHIVED')
    )

    REPORT = 1
    NOT_REPORT = 0

    REPORT_CHOICE = (
        (REPORT, 'Report'),
        (NOT_REPORT, 'Not Report')
    )
    END = 1
    NOT_END = 0

    END_CHOICE = (
        (END, 'End'),
        (NOT_END, 'Not End')
    )

    course = models.ForeignKey(CourseInfo, models.DO_NOTHING, related_name='lesson')
    lesson_no = models.IntegerField()
    unit_no = models.IntegerField(default=1, null=True, blank=True)
    unit_report = models.IntegerField(choices=REPORT_CHOICE, default=NOT_REPORT, blank=True, null=True)
    unit_lesson_no = models.IntegerField(help_text='每节课编号（单元）')
    # unit_end = models.IntegerField(choices=END_CHOICE, default=NOT_END, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def _get_lesson_name(self):
        return 'lesson {0}'.format(self.lesson_no)

    lesson_name = property(_get_lesson_name)

    def __str__(self):
        return '{}-{}'.format(self.course, self.lesson_no)

    class Meta:
        managed = False
        db_table = 'course_lesson'


# class CourseAssessmentQuestion(models.Model):
#     '''课程评估题目'''
#     course = models.ForeignKey(CourseInfo, models.CASCADE, related_name='assessment_question')
#     test_content = models.CharField(max_length=127)
#     test_prefix = models.CharField(max_length=15, help_text='前缀')
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.course
#
#     class Meta:
#         managed = False
#         db_table = 'course_assessment_question'


class CourseAssessmentResult(models.Model):
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE)
    pre_course = models.ForeignKey(CourseInfo, models.DO_NOTHING, related_name='per_assessment_result')
    course = models.ForeignKey(CourseInfo, models.DO_NOTHING, related_name='assessment_result')
    test_level = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    score = models.IntegerField(default=0)
    detail = models.CharField(max_length=4095)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()

    def __str__(self):
        return '{}-{}'.format(self.student_user.real_name, self.course.course_name)

    class Meta:
        managed = False
        db_table = 'course_assessment_result'


class Courseware(models.Model):

    PPT = 1
    IMAGE = 2
    PDF = 3
    COCOS = 5
    TYPE_CHOICE = (
        (PPT, 'PPT'),
        (IMAGE, 'IMAGE'),
        (PDF, 'PDF'),
        (COCOS, 'COCOS')
    )

    lesson = models.ForeignKey(CourseLesson, models.CASCADE)
    cw_type = models.IntegerField(choices=TYPE_CHOICE)
    cw_seq = models.IntegerField()
    # cw_content = models.FileField(upload_to=get_file_path)
    cw_url = models.CharField(max_length=127)
    cw_name = models.CharField(max_length=127, default=None)
    tk_file_id = models.CharField(max_length=31, default=None)
    bj_file_id = models.CharField(max_length=31, default=None)
    tk_file_url = models.CharField(max_length=255, default=None)
    # actual_start_time = models.DateTimeField(null=True, blank=True, help_text='归档开始时间')
    # actual_end_time = models.DateTimeField(null=True, blank=True, help_text='归档结束时间')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.lesson.course.course_name, self.lesson.lesson_no, self.lesson.get_status_display())

    #
    # def save(self, *args, **kwargs):
    #     super(Courseware, self).save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'course_courseware'


class CourseExtcourse(models.Model):

    OLD = 1
    NEW = 2

    COURSE_TYPE_CHOICE = (
        (OLD, 'Old'),
        (NEW, 'New')
    )

    ACTIVE = 1
    ACTIVITY = 2

    COURSE_ACTIVE_CHOICE = (
        (ACTIVE, 'Active'),
        (ACTIVITY, 'Activity')
    )

    PRIVATE = 1
    PUBLIC = 2
    COURSE_STATUS_CHOICE = (
        (PRIVATE, 'Private'),
        (PUBLIC, 'Public'),

    )

    ext_course_name = models.CharField(max_length=63)
    ext_course_type = models.IntegerField(choices=COURSE_TYPE_CHOICE)
    ext_course_status = models.IntegerField(choices=COURSE_STATUS_CHOICE)
    ext_course_tag = models.ForeignKey(CourseExtcourseTag, models.DO_NOTHING, related_name='ext_course')
    ext_course_active = models.IntegerField(choices=COURSE_ACTIVE_CHOICE)
    ext_course_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.ext_course_name, self.get_ext_course_active_display(), self.get_ext_course_status_display())

    class Meta:
        managed = False
        db_table = 'course_extcourse'


class CourseExtcourseOptag(models.Model):
    ext_course = models.ForeignKey(CourseExtcourse, models.DO_NOTHING)
    ext_course_tag = models.ForeignKey(CourseExtcourseTag, models.DO_NOTHING, related_name='ext_course_optag')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_extcourse_optag'


class CourseExtcourseOwner(models.Model):

    '''扩展课件的拥有者'''

    FAVORITE = 1
    NO_FAVORITE = 0

    FAVORITE_CHOICE = (
        (FAVORITE, 'Favorite'),
        (NO_FAVORITE, 'No Favorite')
    )

    tutor_user = models.ForeignKey(TutorInfo, models.DO_NOTHING)
    ext_course = models.ForeignKey(CourseExtcourse, models.DO_NOTHING)
    is_favorite = models.IntegerField(choices=FAVORITE_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_extcourse_owner'


class CourseExtcourseware(models.Model):
    PPT = 1
    IMAGE = 2
    PDF = 3
    ECW_TYPE_CHOICE = (
        (PPT, 'Ppt'),
        (IMAGE, 'Image'),
        (PDF, 'Pdf')
    )
    ext_course = models.ForeignKey(CourseExtcourse, models.DO_NOTHING)
    ecw_type = models.IntegerField(choices=ECW_TYPE_CHOICE)
    ecw_seq = models.IntegerField()
    ecw_url = models.CharField(max_length=127)
    tk_file_id = models.CharField(max_length=31, blank=True, null=True)
    tk_file_url = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_extcourseware'


class CourseHomework(models.Model):

    ACTIVE = 1
    ARCHIVED = 2

    STATUS_CHOICE = (
        (ACTIVE, 'ACTIVE'),
        (ARCHIVED, 'ARCHIVED')
    )

    lesson = models.ForeignKey(CourseLesson, models.DO_NOTHING)
    hw_name = models.CharField(max_length=127)
    hw_content = models.CharField(max_length=127)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.lesson.course.course_name, self.lesson.lesson_no, self.get_status_display())

    class Meta:
        managed = False
        db_table = 'course_homework'


class CourseQuestionnaire(models.Model):

    ACTIVE = 1
    INVALID = 0

    STATUS_CHOICE = (
        (ACTIVE, 'Active'),
        (INVALID, 'Invalid')
    )

    question_no = models.IntegerField()
    title_zh = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, db_column='tilte_en')
    detail = models.CharField(max_length=8192)
    status = models.IntegerField(choices=STATUS_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.question_no, self.get_status_display())

    class Meta:
        managed = False
        db_table = 'course_questionnaire'


class CourseQuestionnaireResult(models.Model):

    student_user = models.ForeignKey(UserStudentInfo, models.DO_NOTHING)
    edition = models.BigIntegerField()
    edition_detail = models.CharField(max_length=511)
    level = models.IntegerField(blank=True, null=True)
    level_detail = models.CharField(max_length=511, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.user.__str__(), self.edition, self.level)

    class Meta:
        managed = False
        db_table = 'course_questionnaire_result'


# class SessionTkfile(models.Model):
#     lesson = models.ForeignKey(CourseLesson, models.DO_NOTHING)
#     tk_file_id = models.CharField(max_length=31)
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return '{}-{}-{}'.format(self.lesson.course.course_name, self.lesson.lesson_no, self.tk_file_id)
#
#     class Meta:
#         managed = False
#         db_table = 'course_session_tkfile'


class CourseTeacherGuidebook(models.Model):
    lesson = models.ForeignKey(CourseLesson, models.CASCADE)
    tp_content = models.CharField(max_length=127)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.lesson.course.course_name, self.lesson.lesson_no)

    class Meta:
        managed = False
        db_table = 'course_teacher_guidebook'


class CourseAssessmentQuestion(models.Model):

    SINGLE = 1
    MULTIPLE = 2
    DRAG = 3
    QUESTION_TYPE_CHOICE = (
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
        (DRAG, 'Drag')  # 连线
    )
    ACTIVE = 1
    ARCHIVED = 2

    STATUS_CHOICE = (
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived')
    )

    course = models.ForeignKey(CourseInfo, models.CASCADE)
    question_no = models.IntegerField()
    question_type = models.IntegerField(choices=QUESTION_TYPE_CHOICE, default=SINGLE)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    degree_of_difficulty = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    detail = models.CharField(max_length=8192)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.question_no, self.course.course_name)

    class Meta:
        managed = False
        db_table = 'course_assessment_question'


class CourseUnit(models.Model):

    '''课程单元配置表'''

    course = models.ForeignKey(CourseInfo, models.CASCADE, related_name='course_unit')
    unit_no = models.IntegerField(null=False, blank=False)
    first_lesson_no = models.IntegerField(default=1, null=False, blank=False)
    last_lesson_no = models.IntegerField(default=1, null=False, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.course, self.unit_no)

    class Meta:
        managed = False
        db_table = 'course_unit'
