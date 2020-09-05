from django.db import models
from django.contrib.auth.models import User


class UserLevel(models.Model):
    PARENT = 1
    CHILDREN = 2
    TEACHER = 3
    AMBASSADOR = 4

    ROLE_CHOICE = (
        (PARENT, 'Parent'),
        (CHILDREN, 'Children'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador')
    )

    FIRST_LEVEL = 1
    SECOND_LEVEL = 2
    THREE_LEVEL = 3
    SUPER_LEVEL = 0

    GRADE_CHOICE = (
        (FIRST_LEVEL, 'first level'),
        (SECOND_LEVEL, 'second level'),
        (THREE_LEVEL, 'three level'),
    )

    role = models.IntegerField()
    grade = models.IntegerField(choices=GRADE_CHOICE)
    remark = models.CharField(max_length=63)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.remark

    class Meta:
        managed = False
        db_table = 'user_level'


class TutorInfo(models.Model):

    '''教师用户信息'''
    DISPLAY = 0  # 展示
    HIDDEN = 1   # 隐藏
    HIDE_CHOICE = (
        (DISPLAY, 'Display'),
        (HIDDEN, 'Hidden')
    )

    MALE = 1
    FEMALE = 2
    UNKNOWN = 0
    GENDER_CHOICE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Unknown')
    )

    NOTACTIVE = 0  # 未激活
    ACTIVE = 1  # 已激活
    FORBIDDEN = 2  # 封禁
    DELETED = 3  # 被删除

    STATUS_CHOICE = (
        (NOTACTIVE, 'Not Active'),
        (ACTIVE, 'Active'),
        (FORBIDDEN, 'Forbidden'),
        (DELETED, 'Deleted')
    )

    ZH = 'ZH'
    EN = 'EN'
    LANGRANGE_CHOICE = (
        (ZH, '中文'),
        (EN, '英文')
    )

    WORKING = 1  # 上岗
    UNWORK = 0   # 未上岗
    WORKING_STATUS = (
        (WORKING, 'Working'),
        (UNWORK, 'Unwork')
    )

    PARENT = 1
    CHILDREN = 2
    TEACHER = 3
    AMBASSADOR = 4

    ROLE_CHOICE = (
        (PARENT, 'Parent'),
        (CHILDREN, 'Children'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador')
    )

    SINGAPORE = 1
    OTHER_AREA = 2
    LOCAL_AREA_CHOICE = (
        (SINGAPORE, 'Singapore'),
        (OTHER_AREA, 'Other Area')
    )

    id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOICE, default=TEACHER)
    username = models.CharField(unique=True, max_length=63, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=31, blank=True, null=True)
    email = models.CharField(unique=True, max_length=63, blank=True, null=True)
    password = models.CharField(max_length=127, blank=True, null=True)
    avatar = models.CharField(max_length=127, blank=True, null=True)
    real_name = models.CharField(max_length=127, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, default=UNKNOWN, blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    nationality = models.CharField(max_length=15, blank=True, null=True)
    country_of_residence = models.CharField(max_length=15, blank=True, null=True)
    currency = models.CharField(max_length=15, blank=True, null=True)
    language = models.CharField(choices=LANGRANGE_CHOICE, default=EN, max_length=31, blank=True, null=True)
    whatsapp = models.CharField(max_length=255, blank=True, null=True)
    wechat = models.CharField(max_length=255, blank=True, null=True)
    description_en = models.CharField(max_length=511, blank=True, null=True)
    description_zh = models.CharField(max_length=511, blank=True, null=True)
    rating_le = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='学习环境')
    rating_id = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='授课方法')
    rating_pk = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='专业知识')
    rating_ot = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='综合评分')
    teaching_start_time = models.DateTimeField(blank=True, null=True, verbose_name='最早从事教学时间')
    total_number_of_class = models.IntegerField(blank=True, null=True, verbose_name='总共上过几节课')
    balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, verbose_name='账户课时余额')
    hide = models.IntegerField(choices=HIDE_CHOICE, default=DISPLAY, blank=True, null=True, verbose_name='是否对学生隐藏')
    working = models.IntegerField(choices=WORKING_STATUS, default=UNWORK, verbose_name='是否上岗')
    last_login_tz = models.CharField(max_length=31, blank=True, null=True, verbose_name='上次登录时区信息')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='上次登陆时间')
    login_tz = models.CharField(max_length=31, blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    is_staff = models.IntegerField(blank=True, null=True, default=0, help_text='是否公司员工，0：不是；1：是')
    working_time = models.DateTimeField(null=True, blank=True)
    # tm_user_id = models.IntegerField(null=True, blank=True, help_text='教师管理用户标识')
    # tm_user_name = models.CharField(max_length=255, null=True, blank=True, help_text='教师管理用户名称')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    highest_degree = models.IntegerField(blank=True, null=True)
    is_school = models.IntegerField(blank=True, null=True)
    training_school = models.CharField(max_length=127, blank=True, null=True)
    training_major = models.CharField(max_length=127, blank=True, null=True)
    bachelor_school = models.CharField(max_length=127, blank=True, null=True)
    bachelor_major = models.CharField(max_length=127, blank=True, null=True)
    master_school = models.CharField(max_length=127, blank=True, null=True)
    master_major = models.CharField(max_length=127, blank=True, null=True)
    doctor_school = models.CharField(max_length=127, blank=True, null=True)
    doctor_major = models.CharField(max_length=127, blank=True, null=True)
    work_start_time = models.DateTimeField(blank=True, null=True)
    current_employer = models.CharField(max_length=127, blank=True, null=True)
    teacher_certificate = models.CharField(max_length=1023, blank=True, null=True)
    teaching_style = models.CharField(max_length=255, blank=True, null=True)
    teaching_grade = models.CharField(max_length=127, blank=True, null=True)
    chinese_level = models.CharField(max_length=63, blank=True, null=True)
    english_level = models.CharField(max_length=63, blank=True, null=True)
    english_listening_speaking_ability = models.CharField(max_length=255, blank=True, null=True)
    other_foreign_language = models.CharField(max_length=255, blank=True, null=True)
    dialect = models.CharField(max_length=127, blank=True, null=True)
    remark = models.CharField(max_length=511, blank=True, null=True)
    identity_number = models.CharField(max_length=31, blank=True, null=True)
    identity_name = models.CharField(max_length=63, blank=True, null=True)
    bank_account_number = models.CharField(max_length=31, blank=True, null=True)
    bank_name = models.CharField(max_length=63, blank=True, null=True)
    bank_branch_name = models.CharField(max_length=127, blank=True, null=True)
    local_area = models.IntegerField(choices=LOCAL_AREA_CHOICE, default=OTHER_AREA, blank=True, null=True)
    full_work = models.IntegerField(default=0, blank=True, null=True, help_text='是否全职，0：不是；1是')

    def __str__(self):
        show_info = ''
        if self.username:
            show_info = self.username
        elif self.email:
            show_info = self.email
        elif self.phone:
            show_info = self.phone
        elif self.real_name:
            show_info = self.real_name
        return show_info

    def add_course(self, course):
        from scheduler.models import ScheduleTutorCourse
        tutor_course = ScheduleTutorCourse()
        tutor_course.tutor_user = self
        tutor_course.course = course
        tutor_course.save()

    def add_class_type(self, class_type):
        from scheduler.models import ScheduleTutorClasstype
        tutor_class_type = ScheduleTutorClasstype()
        tutor_class_type.tutor_user = self
        tutor_class_type.class_type = class_type
        tutor_class_type.save()

    def remove_course(self, course):
        from scheduler.models import ScheduleTutorCourse
        tutor_course = ScheduleTutorCourse.objects.filter(tutor_user=self, course=course).first()
        if tutor_course:
            tutor_course.delete()

    def remove_classtype(self, class_type):
        from scheduler.models import ScheduleTutorClasstype
        tutor_class_type = ScheduleTutorClasstype.objects.filter(tutor_user=self, class_type=class_type).first()
        if tutor_class_type:
            tutor_class_type.delete()

    class Meta:
        managed = False
        db_table = 'user_tutor_info'
