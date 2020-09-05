from django.db import models
from django.utils import timezone
from manage.models import UserInfo


class UserParentInfo(models.Model):

    '''家长用户信息'''

    ZH = 'ZH'
    EN = 'EN'
    LANGRANGE_CHOICE = (
        (ZH, '中文'),
        (EN, '英文')
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

    PARENT = 1
    CHILDREN = 2
    TEACHER = 3
    AMBASSADOR = 4
    STAFF = 5  # 工作人员

    ROLE_CHOICE = (
        (PARENT, 'Parent'),
        (CHILDREN, 'Children'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador'),
        (STAFF, 'Staff')
    )

    id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOICE, default=PARENT)
    username = models.CharField(unique=True, max_length=63, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=31, blank=True, null=True)
    email = models.CharField(unique=True, max_length=63, blank=True, null=True)
    password = models.CharField(max_length=127, blank=True, null=True)
    real_name = models.CharField(max_length=127, blank=True, null=True)
    avatar = models.CharField(max_length=127, blank=True, null=True, verbose_name='verbose_name')
    nationality = models.CharField(max_length=15, blank=True, null=True, verbose_name='国籍， CN SG US')
    country_of_residence = models.CharField(max_length=15, blank=True, null=True, verbose_name='居住国家，CN SG US')
    currency = models.CharField(max_length=15, blank=True, null=True, verbose_name='货币名称')
    language = models.CharField(choices=LANGRANGE_CHOICE, default=EN, max_length=31, blank=True, null=True, verbose_name='偏好语言，中文：ZH；英文：EN，默认EN')
    home_language = models.CharField(max_length=31, blank=True, null=True, verbose_name='家庭主要语言')
    whatsapp = models.CharField(max_length=255, blank=True, null=True)
    wechat = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, verbose_name='账户课时余额')
    bonus_balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, verbose_name='平台奖励课时余额')
    sg_balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, help_text='新加坡小班课余额')
    code = models.CharField(max_length=15, blank=True, null=True, verbose_name='城市合伙人邀请码')
    referrer_user_identify = models.CharField(max_length=63, blank=True, null=True, verbose_name='推荐人用户身份标识')
    referrer_user_id = models.BigIntegerField(blank=True, null=True, verbose_name='推荐人用户标识')
    referrer_user_name = models.CharField(max_length=127, blank=True, null=True, verbose_name='推荐人用户名称')
    adviser_user_id = models.BigIntegerField(blank=True, null=True, verbose_name='顾问用户标识')
    adviser_user_name = models.CharField(max_length=127, blank=True, null=True, verbose_name='顾问用户名称')
    adviser_user_phone = models.CharField(max_length=31, blank=True, null=True, verbose_name='顾问用户电话')
    xg_user_id = models.BigIntegerField(blank=True, null=True, verbose_name='学管id')
    xg_user_name = models.CharField(max_length=127, blank=True, null=True, verbose_name='学管名称')
    xg_user_phone = models.CharField(max_length=31, blank=True, null=True, help_text='学管电话')
    last_login_tz = models.CharField(max_length=31, blank=True, null=True, verbose_name='上次登录时区信息')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='上次登录时间')
    login_tz = models.CharField(max_length=31, blank=True, null=True, verbose_name='最新登录时区信息，默认"+08:00"')
    login_time = models.DateTimeField(blank=True, null=True, verbose_name='最新登录时间')
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

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

    class Meta:
        managed = False
        db_table = 'user_parent_info'


class UserStudentInfo(models.Model):

    '''学生用户信息'''
    MALE = 1
    FEMALE = 2
    UNKNOWN = 0
    GENDER_CHOICE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Unknown')
    )

    UNASSESSED = 0  # 未做过不需要做水平测试
    NEEDASSESSED = 1  # 未做过需要做水平测试
    ASSESSED = 2  # 已做过水平测试
    ASSESSED_CHOICE = (
        (UNASSESSED, '未做过不需要做水平测试'),
        (NEEDASSESSED, '未做过需要做水平测试'),
        (ASSESSED, '已做过水平测试')
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

    TK = 1
    AGARO = 2
    VIRTUALCLASS_TYPE_CHOICE = (
        (TK, 'Tk'),
        (AGARO, 'Agaro')
    )

    FIRST_COURSE = 1
    NOT_FIRST_COURSE = 0
    FIRST_COURSE_CHOICE = (
        (FIRST_COURSE, 'First Course'),
        (NOT_FIRST_COURSE, 'Not First Course')
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

    '''是否开启小班，0：不开启；1开启；默认0'''
    ALLOW_SMALLCLASS = 1
    FORBID_SMALLCLASS = 0

    ALLOW_SMALLCLASS_CHOICE = (
        (ALLOW_SMALLCLASS, 'Allow Smallclass'),
        (FORBID_SMALLCLASS, 'Forbid Smallclass')
    )

    '''上固定小班课，0：否；1：是'''
    ONLY_SMALLCLASS = 1
    NOT_ONLY_SMALLCLASS = 0
    ONLY_SMALLCLASS_CHOICE = (
        (ONLY_SMALLCLASS, 'Only Smallclass'),
        (NOT_ONLY_SMALLCLASS, 'Not Only Smallclass')
    )

    id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOICE, default=CHILDREN, blank=True, null=True)
    avatar = models.CharField(max_length=127, blank=True, null=True)
    real_name = models.CharField(max_length=127, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, default=UNKNOWN, blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    student_parent_user = models.ForeignKey(UserParentInfo, models.DO_NOTHING, related_name='student_children', blank=True, null=True, verbose_name='学生账号家长标识, 为了学生账号解除家长可以单独登陆')
    parent_user = models.ForeignKey(UserParentInfo, models.DO_NOTHING, related_name='children', blank=True, null=True)
    course = models.ForeignKey('course.CourseInfo', models.DO_NOTHING, blank=True, null=True)
    course_edition = models.ForeignKey('course.CourseEdition', models.DO_NOTHING, blank=True, null=True)
    course_level = models.IntegerField(blank=True, null=True)
    lesson = models.ForeignKey('course.CourseLesson', models.DO_NOTHING, blank=True, null=True)
    lesson_no = models.IntegerField(blank=True, null=True)
    assessed = models.IntegerField(choices=ASSESSED_CHOICE, default=UNASSESSED, blank=True, null=True)
    test_level = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    virtualclass_type_id = models.IntegerField(choices=VIRTUALCLASS_TYPE_CHOICE, default=TK, blank=True, null=True)
    first_course = models.IntegerField(choices=FIRST_COURSE_CHOICE, default=FIRST_COURSE, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
    allow_smallclass = models.IntegerField(choices=ALLOW_SMALLCLASS_CHOICE, null=True, blank=True, default=0)
    only_smallclass = models.IntegerField(choices=ONLY_SMALLCLASS_CHOICE, null=True, blank=True)
    create_time = models.DateTimeField(default=timezone.now())
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        # user_parent_info = UserParentInfo.objects.filter(id=self.parent_user_id).only('username').first()
        # return '{}-{}'.format(self.real_name, user_parent_info.username)

        return self.real_name if self.real_name else ''

    class Meta:
        managed = False
        db_table = 'user_student_info'


class AdData(models.Model):

    '''渠道推广注册用户信息'''

    parent_user = models.ForeignKey(UserParentInfo, models.DO_NOTHING)
    custom_s1 = models.CharField(max_length=511, blank=True, null=True)
    custom_s2 = models.CharField(max_length=511, blank=True, null=True)
    custom_s3 = models.CharField(max_length=511, blank=True, null=True)
    utm_source = models.CharField(max_length=511, blank=True, null=True)
    utm_medium = models.CharField(max_length=511, blank=True, null=True)
    utm_campaign = models.CharField(max_length=511, blank=True, null=True)
    utm_term = models.CharField(max_length=511, blank=True, null=True)
    utm_content = models.CharField(max_length=511, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'user_ad_data'


class UserSocialAccount(models.Model):

    '''第三方社交账号'''

    parent_user = models.ForeignKey(UserParentInfo, models.DO_NOTHING)
    provider = models.CharField(max_length=31)
    openid = models.CharField(max_length=63)
    extra_data = models.CharField(max_length=4095)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_social_account'


class UserSocialApp(models.Model):
    provider = models.CharField(max_length=31)
    name = models.CharField(max_length=31)
    client_id = models.CharField(max_length=31)
    secret = models.CharField(max_length=31)
    key = models.CharField(max_length=31)
    site = models.CharField(max_length=63, blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_social_app'


class UserSocialToken(models.Model):

    '''第三方社交账号token'''

    app = models.ForeignKey(UserSocialApp, models.DO_NOTHING, verbose_name='APP标识')
    account = models.ForeignKey(UserSocialAccount, models.DO_NOTHING, verbose_name='社交账号标识')
    token = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    expire_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'user_social_token'


class UserIp(models.Model):

    '''真实ip跟代理ip表'''

    PARENT = 1
    CHILDREN = 2
    TEACHER = 3
    AMBASSADOR = 4
    STAFF = 5  # 工作人员

    ROLE_CHOICE = (
        (PARENT, 'Parent'),
        (CHILDREN, 'Children'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador'),
        (STAFF, 'Staff')
    )

    real_ip = models.CharField(max_length=32, null=False, blank=False, verbose_name='真实ip')
    username = models.CharField(max_length=127, null=False, blank=False, verbose_name='用户名')
    role = models.IntegerField(choices=ROLE_CHOICE, null=False, blank=False, verbose_name='角色')
    country = models.CharField(max_length=32, null=True, blank=True, verbose_name='国家')
    country_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='国家id')
    region = models.CharField(max_length=32, null=True, blank=True, verbose_name='省份')
    region_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='省份id')
    city = models.CharField(max_length=32, null=True, blank=True, verbose_name='城市')
    city_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='城市id')
    longitude = models.CharField(max_length=32, null=True, blank=True, help_text='经度')
    latitude = models.CharField(max_length=32, null=True, blank=True, help_text='纬度')
    access_times = models.IntegerField(null=True, blank=True, help_text='访问次数')
    parent_user_id = models.BigIntegerField(null=True, blank=True, help_text='家长id')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'user_ip'


class StudentRemark(models.Model):

    user = models.ForeignKey(UserInfo, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=200, default='', verbose_name='备注内容')
    create_time = models.DateTimeField(auto_now_add=True)
    student_id = models.BigIntegerField(verbose_name='学生id')

    class Meta:
        db_table = 'manager_student_remark'


class ExtStudent(models.Model):

    PAY_ACTION = (
        (1, '低'),
        (2, '中'),
        (3, '高')
    )

    NO_RECORD = 3

    CHINESE_ENV = 1
    NOT_CHINESE_ENV = 2
    HAS_CHINESE_ENV_CHOICE = (
        (CHINESE_ENV, '是'),
        (NOT_CHINESE_ENV, '否'),
        (NO_RECORD, '未记录')
    )

    MALE = 1
    FEMALE = 2

    GENDER_CHOICE = (
        (MALE, '男'),
        (FEMALE, '女'),
        (NO_RECORD, '未记录')
    )

    CAN_APPOINtMENT = 1
    NOT_CAN_APPOINTMENT = 2

    APPOINTMENT_CHOICE = (
        (CAN_APPOINtMENT, '是'),
        (NOT_CAN_APPOINTMENT, '否'),
        (NO_RECORD, '未记录')
    )

    CHANGE_TEACHER = 1
    NOT_CHANGE_TEACHER = 2

    CHANGE_TEACHER_CHOICE = (
        (CHANGE_TEACHER, '是'),
        (NOT_CHANGE_TEACHER, '否'),
        (NO_RECORD, '未记录')
    )

    student_id = models.BigIntegerField()
    weixin = models.CharField(max_length=30, null=True, blank=True)
    whatsapp = models.CharField(max_length=30, null=True, blank=True)
    class_year = models.CharField(max_length=30, null=True, blank=True, verbose_name='年级')
    school = models.CharField(max_length=30, null=True, blank=True)
    school_nature = models.CharField(max_length=30, null=True, blank=True, verbose_name='学校性质')
    # course_adviser = models.ForeignKey(CmsUser, null=True, blank=True, related_name='course_adviser', verbose_name='课程顾问')
    source_channel = models.CharField(max_length=30, null=True, blank=True, verbose_name='来源渠道')
    # learn_manager = models.ForeignKey(CmsUser, null=True, blank=True, related_name='learn_manager', verbose_name='学管老师')
    pay_action = models.SmallIntegerField(choices=PAY_ACTION, default=1, verbose_name='付费意向')
    age = models.SmallIntegerField(null=True, blank=True, verbose_name='年龄')
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='年龄')
    student_location = models.CharField(max_length=100, null=True, blank=True, verbose_name='学生所在地')
    equipment = models.CharField(max_length=50, null=True, blank=True, verbose_name="上课设备")
    test_result = models.CharField(max_length=30, null=True, blank=True, verbose_name="检测结果")
    test_time = models.DateTimeField(null=True, blank=True, verbose_name="检测时间")

    # 新增字段
    student_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='学生姓名')
    reference_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='推荐人')
    gender = models.SmallIntegerField(choices=GENDER_CHOICE, default=NO_RECORD, null=True, blank=True, verbose_name='性别')
    teacher = models.CharField(max_length=50, null=True, blank=True, verbose_name='授课老师')
    teach_time = models.CharField(max_length=50, null=True, blank=True, verbose_name='授课时间')
    study_time = models.CharField(max_length=50, null=True, blank=True, verbose_name='上课固定时间')
    nature = models.CharField(max_length=50, null=True, blank=True, verbose_name='性格')
    hobby = models.CharField(max_length=50, null=True, blank=True, verbose_name='兴趣爱好')
    favorite_subject = models.CharField(max_length=50, null=True, blank=True, verbose_name='喜欢的学科')
    can_appointment = models.SmallIntegerField(choices=APPOINTMENT_CHOICE, default=NO_RECORD, null=True, blank=True, verbose_name='是否可以自行约课')
    change_teacher = models.SmallIntegerField(choices=CHANGE_TEACHER_CHOICE, default=NO_RECORD, null=True, blank=True, verbose_name='是否需要更换老师')
    has_chinese_env = models.SmallIntegerField(choices=HAS_CHINESE_ENV_CHOICE, default=NO_RECORD, null=True, blank=True, verbose_name='日常是否有中文环境')
    study_target = models.CharField(max_length=50, null=True, blank=True, verbose_name='学习中文目的')
    learning_brother = models.SmallIntegerField(null=True, blank=True, verbose_name='在平台学习的兄弟姐妹数量')
    feedback = models.CharField(max_length=500, null=True, blank=True, verbose_name='课程顾问沟通反馈')

    parental_expectation = models.CharField(max_length=500, null=True, blank=True, verbose_name='家长期望')
    #  新增字段

    literacy = models.CharField(max_length=255, null=True, blank=True, verbose_name='大概识字量')
    write_amount = models.CharField(max_length=255, null=True, blank=True, verbose_name='大概写字量')
    pinyin = models.CharField(max_length=255, null=True, blank=True, verbose_name='是否学过拼音')
    chinese_experience = models.CharField(max_length=255, null=True, blank=True, verbose_name='中文学习经历')
    listen_speak_ability = models.CharField(max_length=255, null=True, blank=True, verbose_name='中文听说能力')
    language_environment = models.CharField(max_length=255, null=True, blank=True, verbose_name='家庭语言环境')
    edit_user_id = models.IntegerField(null=True, blank=True, verbose_name='编辑人')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manager_ext_student'
        unique_together = ('student_id', )


class UserSource(models.Model):

    parent_user = models.ForeignKey(UserParentInfo, primary_key=True, related_name='user_source')
    channel = models.CharField(max_length=15, null=False, blank=False, help_text='渠道 wecaht，web，ios，android')
    activity_code = models.CharField(max_length=8, null=False, blank=True, default='', help_text='活动编码 none:无，referrer:转介绍，bigclass大班课')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_source'
