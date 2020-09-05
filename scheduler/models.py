from django.db import models
from tutor.models import UserLevel, TutorInfo
from student.models import UserStudentInfo, UserParentInfo
from course.models import CourseInfo, CourseLesson, CourseEdition
from classroom.models import ClassInfo, ClassType, VirtualclassInfo
from . import app_settings


class StudentTimetable(models.Model):

    '''学生课表'''

    CANCELED_PUBLISH = 0
    SUCCESS_APPOINTMENT = 1
    PUBLISHED = 2
    OCCUPATION = 3

    STATUS_CHOICE = (
        (CANCELED_PUBLISH, 'Canceled Publish'),
        (SUCCESS_APPOINTMENT, 'Succed Appoint'),
        (PUBLISHED, 'Published'),
        (OCCUPATION, 'Occupation')
    )

    id = models.BigIntegerField(primary_key=True)
    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE)
    class_type = models.ForeignKey(ClassType, models.CASCADE)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE, related_name='student_time_table')
    class_field = models.ForeignKey(ClassInfo, models.DO_NOTHING, db_column='class_id', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_student_timetable'


class ScheduleTutorClasstype(models.Model):

    '''教师可上课的班级类型'''

    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE, related_name='tutor_class_type')
    class_type = models.ForeignKey(ClassType, models.CASCADE, related_name='tutor_users')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_tutor_classtype'


class ScheduleTutorCourse(models.Model):

    '''教师可上课的课程'''

    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE, related_name='tutor_course')
    course = models.ForeignKey(CourseInfo, models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_tutor_course'


class ScheduleTutorLevel(models.Model):

    '''教师各个版本的级别'''

    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE, related_name='tutor_level')
    course_edition = models.ForeignKey(CourseEdition, models.DO_NOTHING)
    user_level = models.ForeignKey(UserLevel, models.DO_NOTHING)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_tutor_level'


class TutorTimetable(models.Model):

    CANCELED_PUBLISH = 0
    SUCCESS_APPOINTMENT = 1
    PUBLISHED = 2
    OCCUPATION = 3

    STATUS_CHOICE = (
        (CANCELED_PUBLISH, 'Canceled Publish'),
        (SUCCESS_APPOINTMENT, 'Succed Appoint'),
        (PUBLISHED, 'Published'),
        (OCCUPATION, 'Occupation')
    )

    id = models.BigIntegerField(primary_key=True)
    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE, related_name='tutor_time_table')
    class_type = models.ForeignKey(ClassType, models.CASCADE, blank=True, null=True)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE, blank=True, null=True)
    class_field = models.ForeignKey(ClassInfo, models.CASCADE, db_column='class_id', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=PUBLISHED)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    default_event_duration = app_settings.EVENT_DURATION

    class Meta:
        managed = False
        db_table = 'schedule_tutor_timetable'


class ScheduleVirtualclassMember(models.Model):

    '''课堂学生进入时间'''

    NO = 0
    YES = 1
    FIRST_COURSE_CHOICE = (
        (NO, 'No'),
        (YES, 'Yes')
    )

    STUDENT = 1
    TEACHER = 2
    AMBASSADOR = 3

    ROLE_CHOICE = (
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador')
    )

    BOTH_FIRST = 1
    NOT_BOTH_FIRST = 0

    BOTH_FIRST_CHOICE = (
        (BOTH_FIRST, 'Both First Course'),
        (NOT_BOTH_FIRST, 'Not Both First Course')
    )

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE, blank=True, null=True, related_name='virtual_class_member')
    student_timetable = models.ForeignKey(StudentTimetable, models.CASCADE)
    class_field = models.ForeignKey(ClassInfo, models.DO_NOTHING, db_column='class_id')  # Field renamed because it was a Python reserved word.
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE, related_name='virtual_class_member')
    class_type_id = models.IntegerField()
    first_course = models.IntegerField(choices=FIRST_COURSE_CHOICE, default=NO, blank=True, null=True)
    both_first_course = models.IntegerField(choices=BOTH_FIRST_CHOICE, default=NOT_BOTH_FIRST, blank=True, null=True)
    start_time = models.DateTimeField()
    enter_time = models.DateTimeField(blank=True, null=True)
    leave_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_virtualclass_member'


class ScheduleClassTimeTable(models.Model):

    SUCCESS_APPOINTMENT = 1
    PUBLISHED = 2
    CANCELD_PUBLISHED = 0

    STATUS_CHOICE = (
        (SUCCESS_APPOINTMENT, 'Success Appointment'),
        (PUBLISHED, 'Published'),
        (CANCELD_PUBLISHED, 'Canceld publishd')
    )

    class_field = models.ForeignKey(ClassInfo, models.CASCADE, db_column='class_id')  # Field renamed because it was a Python reserved word.
    # tutor_user = models.ForeignKey(TutorInfo, models.CASCADE, null=True, blank=True)
    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE, null=True, blank=True, related_name='class_timetable')
    start_time = models.DateTimeField(help_text='上课时间')
    end_time = models.DateTimeField(help_text='下课时间')
    appoint_user_id = models.IntegerField(help_text='约课人')
    appoint_user_name = models.CharField(max_length=127)
    # appoint_time = models.DateTimeField(help_text='预排课时间')
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=PUBLISHED)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'schedule_class_timetable'



