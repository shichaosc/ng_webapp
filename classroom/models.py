import logging
from django.db import models
from course.models import CourseExtcourse, CourseLesson, CourseEdition, CourseInfo
from student.models import UserStudentInfo
from tutor.models import TutorInfo
from course.models import CourseHomework
from django.conf import settings
from manage.models import UserInfo

logger = logging.getLogger(__name__)

api_key = '45569802'
api_secret = 'bd18d53d03b50222656a397686c364445900d5f9'

appID = settings.AGORA_APP_ID
appCertificate = settings.AGORA_APP_CERTIFICATE

PROVIDER_OPENTOK = 'OPENTOK'
PROVIDER_AGORA = 'AGORA.IO'


class ClassInfo(models.Model):

    '''班型标识，1：1对1；2：小班课；3：大班课；默认值2'''

    FIRST_COURSE = 1
    NOT_FIRST_COURSE = 0

    FIRST_COURSE_CHOICE = (
        (FIRST_COURSE, 'First Course'),
        (NOT_FIRST_COURSE, 'Not First Course')
    )

    ONE2ONE = 1
    SMALL_CLASS = 2
    BIG_CLASS = 3
    CLASS_TYPE_CHOICE = (
        (ONE2ONE, 'One2One'),
        (SMALL_CLASS, 'Small_Class'),
        (BIG_CLASS, 'Big_Class')
    )

    FREE_SMALLCLASS = 1  # 免费
    SINGAPORE_SMALLCLASS = 2  # 新加坡小班课
    EURO_SMALLCLASS = 3  # 亚欧小班课

    CHARGE_RULE_CHOICES = (
        (FREE_SMALLCLASS, 'Free Smallclass'),
        (SINGAPORE_SMALLCLASS, 'Singapore Smallclass'),
        (EURO_SMALLCLASS, 'Euro Smallclass')
    )

    id = models.BigIntegerField(primary_key=True)
    class_no = models.CharField(max_length=64, help_text='班级编号')
    creator_user = models.ForeignKey(UserStudentInfo, models.DO_NOTHING, related_name='create_class_info', verbose_name='创建者的用户标识', null=True, blank=True)
    leader_user = models.ForeignKey(UserStudentInfo, models.DO_NOTHING, related_name='leader_class_info', verbose_name='班长的用户标识', null=True, blank=True)
    class_type_id = models.IntegerField(choices=CLASS_TYPE_CHOICE, default=SMALL_CLASS)
    user_max = models.IntegerField(default=11, verbose_name='班级最大人数')
    user_num = models.IntegerField(verbose_name='班级当前人数')
    class_name = models.CharField(max_length=127, blank=True, null=True)
    class_name_zh = models.CharField(max_length=127, blank=True, null=True)
    schedule_time_range = models.CharField(max_length=127, blank=True, null=True, help_text='上课时间')
    course = models.ForeignKey(CourseInfo, models.DO_NOTHING, blank=True, null=True)
    course_edition = models.ForeignKey(CourseEdition, models.DO_NOTHING, blank=True, null=True)
    course_level = models.IntegerField(blank=True, null=True)
    lesson = models.ForeignKey(CourseLesson, models.DO_NOTHING, blank=True, null=True)
    lesson_no = models.IntegerField(blank=True, null=True)
    class_category = models.SmallIntegerField(choices=CHARGE_RULE_CHOICES, null=True, default=True)
    first_course = models.IntegerField(choices=FIRST_COURSE_CHOICE, default=NOT_FIRST_COURSE, help_text='是否首次课，0：不是；1是，默认0')
    create_user_id = models.IntegerField(null=True, blank=True, help_text='班级创建人id')
    create_user_name = models.CharField(max_length=127, null=True, blank=True, help_text='班级创建人名字')
    # package = models.ForeignKey(CoursePackage, null=True, blank=True)
    student_area = models.CharField(max_length=255, null=True, blank=True, help_text='招生地区')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_name_zh

    class Meta:
        managed = False
        db_table = 'classroom_class_info'


class ClassType(models.Model):

    ONE2ONE = 1
    SMALLCLASS = 2
    BIGCLASS =3

    name = models.CharField(max_length=31)
    user_max = models.IntegerField()
    description = models.CharField(max_length=4095)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'classroom_class_type'


class VirtualclassType(models.Model):

    TK = 1
    BAIJIAYUN = 2

    name = models.CharField(max_length=31)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'classroom_virtualclass_type'


class VirtualclassInfo(models.Model):

    NORMAL = 0
    STUDENT_ABSENCE = 1  # 学生缺席
    STUDENT_EQUIPMENT_ABNORMAL = 2  # 学生设备或网络故障
    STUDENT_CANCELD = 3  # 被学生取消
    TUTOR_ABSENCE = 11  # 教师缺席
    TUTOR_EQUIPMENT_ABNORMAL = 12  # 老师设备或网络故障
    OTHER_REASON = 20  # 其他
    CLASS_NOONE = 21  # 学生老师均未出席
    TUTOR_NOT_FINISH =22  # 老师未点击授课结束

    REASON_CHOICE = (
        (NORMAL, 'Normal'),
        (STUDENT_ABSENCE, 'Student Absence'),
        (STUDENT_CANCELD, 'Student Canceld'),
        (TUTOR_ABSENCE, 'Tutor Absence'),
        (TUTOR_EQUIPMENT_ABNORMAL, 'Tutor Equipment Abnormal'),
        (OTHER_REASON, 'Other Reason'),
        (CLASS_NOONE, 'Class No One'),
        (TUTOR_NOT_FINISH, 'Tutor not Finish')
    )


    CANCELED = 0   # 取消上课
    NOT_START = 1   # 未开始
    STARTED = 2    # 正在开始
    FINISH_NOMAL = 3   # 正常结束
    FINISH_ABNOMAL = 4   # 异常结束

    STATUS_CHOICE = (
        (CANCELED, 'Canceled'),
        (NOT_START, 'Not Start'),
        (STARTED, 'Started'),
        (FINISH_NOMAL, 'Finish Nomal'),
        (FINISH_ABNOMAL, 'Finish Abnomal')
    )


    FIRST_COURSE = 1
    NOT_FIRST_COURSE = 0

    FIRST_COURSE_CHOICE = (
        (FIRST_COURSE, 'First Course'),
        (NOT_FIRST_COURSE, 'Not First Course')
    )

    UNIT_REPORT = 1
    NOT_UNIT_REPORT = 0

    UNIT_REPORT_CHOICE = (
        (UNIT_REPORT, 'Unit Report'),
        (NOT_UNIT_REPORT, 'Not Unit Report')
    )

    '''成功预约用户角色，2：学生；3：老师；5：运营人员'''

    STUDENT = 2
    TUTOR = 3
    MANAGER = 5

    OPS_ROLE_CHOICE = (
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
        (MANAGER, 'Manager')
    )

    id = models.BigIntegerField(primary_key=True)
    absent_tutor_user = models.ForeignKey(TutorInfo, on_delete=models.CASCADE, null=True, blank=True)
    tutor_user = models.ForeignKey(TutorInfo, on_delete=models.CASCADE, related_name='virtual_class')
    lesson = models.ForeignKey(CourseLesson, models.CASCADE, blank=True, null=True, related_name='virtualclass_info')
    lesson_no = models.IntegerField(blank=True, null=True)
    virtualclass_type = models.ForeignKey(VirtualclassType, models.CASCADE)
    class_type = models.ForeignKey(ClassType, models.CASCADE)
    class_field = models.ForeignKey(ClassInfo, models.CASCADE, db_column='class_id', blank=True, null=True, related_name='virtualclass_info')  # Field renamed because it was a Python reserved word.
    # unit_report = models.IntegerField(choices=UNIT_REPORT_CHOICE, null=True, blank=True)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE, null=True, blank=True, verbose_name='约课的学生')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    actual_start_time = models.DateTimeField(blank=True, null=True)
    actual_end_time = models.DateTimeField(blank=True, null=True)
    first_course = models.IntegerField(choices=FIRST_COURSE_CHOICE, default=NOT_FIRST_COURSE, help_text='是否首次课，0：不是；1是，默认0')
    status = models.IntegerField(choices=STATUS_CHOICE, default=NOT_START, help_text='状态，0：已取消；1：未开始；2：开始上课；3：正常结束；4：异常结束')
    ops_role = models.IntegerField(choices=OPS_ROLE_CHOICE, blank=True, null=True, help_text='成功预约用户角色，2：学生；3：老师；5：运营人员')
    tk_class_id = models.CharField(max_length=127, blank=True, null=True)
    tk_replay_url = models.CharField(max_length=2047, blank=True, null=True)
    bj_class_id = models.CharField(max_length=127, null=True, blank=True)
    bj_replay_url = models.CharField(max_length=2047, null=True, blank=True)
    reason = models.IntegerField(choices=REASON_CHOICE, blank=True, null=True)
    remark = models.CharField(max_length=4095, blank=True, null=True)
    duration = models.IntegerField(default=55, help_text='时长，单位分钟')
    remove = models.IntegerField(null=True, blank=True, default=0, help_text='是否删除 0:正常，1:删除，默认:0')
    # package_id = models.IntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def _get_api_key(self):
        return api_key

    api_key = property(_get_api_key)

    @property
    def students(self):
        if self.class_type_id == ClassType.BIGCLASS:
            return []
        members = self.virtual_class_member.all()
        return [member.student_user.real_name for member in members]

    ROLE_TUTOR = 'tutor'
    ROLE_STUDENT = 'student'

    # def get_token_id(self, username, role=ROLE_STUDENT):
    #     if settings.VIDEO_SERVICE_PROVIDER == PROVIDER_AGORA:
    #         return None
    #
    #     opentok = OpenTok(api_key, api_secret)
    #     session_id = self.session_id
    #
    #     if not session_id:
    #         return None
    #
    #     connectionMetadata = '{"role":"' + role + '", "username":"' + username + '"}'
    #
    #     if role == self.ROLE_TUTOR:
    #         token_id = opentok.generate_token(session_id, Roles.moderator, None, connectionMetadata)
    #         logger.debug('generate token for moderator')
    #     else:
    #         token_id = opentok.generate_token(session_id, Roles.publisher, None, connectionMetadata)
    #         logger.debug('generate token for publisher')
    #     return token_id

    # def get_video_service_provider(self):
    #
    #     if settings.VIDEO_SERVICE_PROVIDER:
    #         default_provider = settings.VIDEO_SERVICE_PROVIDER
    #     else:
    #         default_provider = PROVIDER_AGORA
    #
    #     session_id = self.session_id
    #
    #     if not session_id:
    #         return PROVIDER_AGORA
    #     else:
    #         return default_provider

    class Meta:
        permissions = (
            ("can_monitor_virtualclass", "Can monitor virtualclass"),
        )
        managed = False
        db_table = 'classroom_virtualclass_info'
    #
    # def __str__(self):
    #     if self.class_field:
    #         return '{} - {} - {}'.format(self.start_time, self.tutor_user, self.student_user)
    #     else:
    #         from scheduler.models import ScheduleVirtualclassMember
    #
    #         members = ScheduleVirtualclassMember.objects.filter(virtual_class=self).all()
    #         return '{} - {} - {}'.format(self.start_time, self.tutor_user, ','.join([i.student_user.parent_user.username for i in members]))


class ClassMember(models.Model):
    '''班长成员角色，0：已退出班级；1：班长；2：成员'''
    QUITED = 0
    MONITOR = 1
    MEMBER = 2

    ROLE_CHOICE = (
        (QUITED, 'exited class'),
        (MONITOR, 'Monitor'),
        (MEMBER, 'Member')
    )

    class_field = models.ForeignKey(ClassInfo, models.CASCADE, db_column='class_id', related_name='class_member')  # Field renamed because it was a Python reserved word.
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICE, default=MONITOR)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'classroom_class_member'


class VirtualclassComment(models.Model):

    '''课堂评论'''

    PARENT = 1
    STUDENT = 2
    TEACHER = 3
    AMBASSADOR = 4

    ROLE_CHOICE = (
        (PARENT, 'Parent'),
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (AMBASSADOR, 'Ambassador')
    )

    EASY = 1
    MIDDLE = 2
    DIFFICULT = 3

    DIFFICULT_LEVEL_CHOICE = (
        (EASY, 'Easy'),
        (MIDDLE, 'Middle'),
        (DIFFICULT, 'Difficult')
    )

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICE, verbose_name='提交评价的用户角色')
    tutor_user = models.ForeignKey(TutorInfo, models.DO_NOTHING)
    student_user = models.ForeignKey(UserStudentInfo, models.DO_NOTHING)
    comment_en = models.CharField(max_length=1023, blank=True, null=True)
    comment_zh = models.CharField(max_length=1023, blank=True, null=True)
    rating_le = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='学习环境/学习态度')
    rating_id = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='授课方法/进步程度')
    rating_pk = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='专业知识/知识掌握程度')
    difficult_level = models.SmallIntegerField(choices=DIFFICULT_LEVEL_CHOICE, null=True, blank=True, help_text='课堂难易程度，1：较简单；2：适中；3：较难')
    suggestion = models.CharField(max_length=2047, null=True, blank=True, help_text='对本堂课的建议')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'classroom_virtualclass_comment'


class VirtualclassResource(models.Model):

    '''课堂课件资源'''

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE)
    ext_course = models.ForeignKey(CourseExtcourse, models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'classroom_virtualclass_resource'


class VirtualclassHomeworkResult(models.Model):

    '''家庭作业结果'''

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE)
    homework = models.ForeignKey(CourseHomework, models.CASCADE)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE)
    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE)
    score = models.IntegerField(blank=True, null=True, verbose_name='评分')
    comment_en = models.CharField(max_length=1023, blank=True, null=True, verbose_name='英文评论')
    comment_zh = models.CharField(max_length=1023, blank=True, null=True, verbose_name='中文评论')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.virtual_class_id, self.student_user.real_name)

    class Meta:
        managed = False
        db_table = 'classroom_virtualclass_homework_result'


class VirtualclassHomeworkAttachment(models.Model):

    '''家庭作业结果的文件附件'''

    TEXT = 1
    FILE = 2
    AUDIO = 3
    VIDEO = 4
    ATTACHMENT_CHOICE = (
        (TEXT, 'Text'),
        (FILE, 'File'),
        (AUDIO, 'Audio'),
        (VIDEO, 'Video')
    )

    virtual_class = models.ForeignKey(VirtualclassInfo, models.DO_NOTHING)
    homework_result = models.ForeignKey(VirtualclassHomeworkResult, models.DO_NOTHING)
    attachment_type = models.IntegerField(choices=ATTACHMENT_CHOICE, default=FILE, verbose_name='附件类型')
    attachment = models.CharField(max_length=1023, verbose_name='作业结果文件路径')
    length = models.IntegerField(blank=True, null=True, verbose_name='附件大小')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'classroom_virtualclass_homework_attachment'


class VirtualclassFirstReport(models.Model):

    '''首次课报告表'''

    NOT_COMMIT = 0
    COMMITED = 1
    EXAMINE_FAILD = 2
    EXAMINED = 3
    SAVED = 4

    STATUS_CHOICE = (
        (NOT_COMMIT, 'Not Commit'),
        (COMMITED, 'Commited'),
        (EXAMINE_FAILD, 'Examine Faild'),
        (EXAMINED, 'Examined'),
        (SAVED, 'Saced')
    )

    READ = 1
    NOT_READ = 0
    REDA_STATUS_CHOICE = (
        (READ, 'Read'),
        (NOT_READ, 'Not Read')
    )

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE)
    start_time = models.DateTimeField()
    class_type = models.ForeignKey(ClassType, models.CASCADE)
    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE)
    course_info_en = models.CharField(max_length=255, default=None, verbose_name='英文本次课文选用')
    course_info_zh = models.CharField(max_length=255, default=None, verbose_name='中文本次课文选用')
    core_knowledge_en = models.CharField(max_length=1023, default=None, verbose_name='英文核心知识点与课堂要求')
    core_knowledge_zh = models.CharField(max_length=1023, default=None, verbose_name='中文核心知识点与课堂要求')
    add_knowledge_en = models.CharField(max_length=1023, default=None, verbose_name='英文补充知识点')
    add_knowledge_zh = models.CharField(max_length=1023, default=None, verbose_name='中文补充知识点')
    classroom_feedback_en = models.CharField(max_length=1023, default=None, verbose_name='英文本次课堂反馈')
    classroom_feedback_zh = models.CharField(max_length=1023, default=None, verbose_name='中文本次课堂反馈')
    communication_suggestion_en = models.CharField(max_length=1023, default=None, verbose_name='英文与家长沟通及建议')
    communication_suggestion_zh = models.CharField(max_length=1023, default=None, verbose_name='中文与家长沟通及建议')
    suggest_course_info_en = models.CharField(max_length=255, default=None, verbose_name='英文建议教材等级与课时')
    suggest_course_info_zh = models.CharField(max_length=255, default=None, verbose_name='中文建议教材等级与课时')
    student_character_en = models.CharField(max_length=1023, default=None, verbose_name='英文学生性格')
    student_character_zh = models.CharField(max_length=1023, default=None, verbose_name='中文学生性格')
    student_background_en = models.CharField(max_length=1023, default=None, verbose_name='英文学生其他背景')
    student_background_zh = models.CharField(max_length=1023, default=None, verbose_name='中文学生其他背景')
    advisor_assistance_en = models.CharField(max_length=1023, default=None, verbose_name='英文需要课程顾问协助')
    advisor_assistance_zh = models.CharField(max_length=1023, default=None, verbose_name='中文需要课程顾问协助')
    status = models.IntegerField(choices=STATUS_CHOICE, default=NOT_COMMIT, null=False)
    read_status = models.IntegerField(choices=REDA_STATUS_CHOICE, default=0)
    submit_count = models.IntegerField(default=0, null=False, verbose_name='累计提交次数')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_first_report'


class VirtualclassUnitReport(models.Model):

    '''单元报告表'''

    NOT_COMMIT = 0
    COMMITED = 1
    EXAMINE_FAILD = 2
    EXAMINED = 3
    SAVED = 4

    STATUS_CHOICE = (
        (NOT_COMMIT, 'Not Commit'),
        (COMMITED, 'Commited'),
        (EXAMINE_FAILD, 'Examine Faild'),
        (EXAMINED, 'Examined'),
        (SAVED, 'Saved')
    )

    READ = 1
    NOT_READ = 0
    REDA_STATUS_CHOICE = (
        (READ, 'Read'),
        (NOT_READ, 'Not Read')
    )

    virtual_class = models.ForeignKey(VirtualclassInfo, models.CASCADE)
    class_type = models.ForeignKey(ClassType, models.CASCADE)
    class_field = models.ForeignKey(ClassInfo, models.CASCADE, db_column='class_id', related_name='class_unitreport')  # Field renamed because it was a Python reserved word.
    unit_no = models.IntegerField(verbose_name='单元编号')
    first_lesson_no = models.IntegerField(default=1, verbose_name='本单元第一课')
    last_lesson_no = models.IntegerField(default=1, verbose_name='本单元最后一课')
    first_start_time = models.DateTimeField(verbose_name='学生上该单元第一次课的时间')
    last_start_time = models.DateTimeField(verbose_name='学生上该单元最后一次课的时间')
    tutor_user = models.ForeignKey(TutorInfo, models.CASCADE)
    student_user = models.ForeignKey(UserStudentInfo, models.CASCADE)
    skill_assessment_en = models.CharField(max_length=1023, verbose_name="英文技能测评结果")
    skill_assessment_zh = models.CharField(max_length=1023, verbose_name="中文技能测评结果")
    classroom_performance_en = models.CharField(max_length=2047, verbose_name="英文课堂表现")
    classroom_performance_zh = models.CharField(max_length=2047, verbose_name="中文课堂表现")
    improvement_point_en = models.CharField(max_length=2047, verbose_name="英文提升空间改进点")
    improvement_point_zh = models.CharField(max_length=2047, verbose_name="中文提升空间改进点")
    learning_suggestion_en = models.CharField(max_length=2047, verbose_name="英文学习建议")
    learning_suggestion_zh = models.CharField(max_length=2047, verbose_name="中文学习建议")
    status = models.IntegerField(choices=STATUS_CHOICE, default=NOT_COMMIT, null=False)
    submit_count = models.IntegerField(default=0, null=False, verbose_name='累计提交次数')
    read_status = models.IntegerField(choices=REDA_STATUS_CHOICE, default=0)
    remark = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    remark_user_id = models.IntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_unit_report'


class VirtualclassUnitReportAudit(models.Model):

    EXAMINE_FAILD = 2
    EXAMINED = 3
    SAVED = 4

    STATUS_CHOICE = (
        (EXAMINE_FAILD, 'Examine Faild'),
        (EXAMINED, 'Examined'),
        (SAVED, 'Saved')
    )

    unit_report = models.ForeignKey(VirtualclassUnitReport, related_name='unit_report_audit')
    audit_user_id = models.IntegerField()
    audit_user_name = models.CharField(max_length=127)
    remark = models.CharField(max_length=1023)
    status = models.IntegerField(choices=STATUS_CHOICE, help_text='审核状态，2：审核不通过；3：审核通过')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_unit_report_audit'


class VirtualclassFirstReportAudit(models.Model):

    EXAMINE_FAILD = 2
    EXAMINED = 3
    SAVED = 4

    STATUS_CHOICE = (
        (EXAMINE_FAILD, 'Examine Faild'),
        (EXAMINED, 'Examined'),
        (SAVED, 'Saved')
    )

    first_report = models.ForeignKey(VirtualclassFirstReport, related_name='first_report_audit')
    audit_user_id = models.IntegerField()
    audit_user_name = models.CharField(max_length=127)
    remark = models.CharField(max_length=1023)
    status = models.IntegerField(choices=STATUS_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_first_report_audit'


def get_video_service_provider(virtual_class):
    if settings.VIDEO_SERVICE_PROVIDER:
        default_provider = settings.VIDEO_SERVICE_PROVIDER
    else:
        default_provider = PROVIDER_AGORA

    try:
        session_id = virtual_class.session_id
    except AttributeError:
        try:
            vc = VirtualclassInfo.objects.get(id=virtual_class)
            session_id = vc.session_id
        except VirtualclassInfo.DoesNotExist:
            return None

    if not session_id:
        return PROVIDER_AGORA
    else:
        return default_provider


class CourseReportFine(models.Model):

    '''学习报告罚金表'''

    UNIT_REPORT = 1
    FIRST_REPORT = 2
    TYPE_CHOICE = (
        (UNIT_REPORT, 'Unit Report'),
        (FIRST_REPORT, 'First Report')
    )

    user = models.ForeignKey(UserInfo, on_delete=models.DO_NOTHING)
    report_id = models.IntegerField()
    type = models.SmallIntegerField(choices=TYPE_CHOICE)
    money = models.IntegerField()
    remark = models.CharField(max_length=255, null=True, blank=True, verbose_name='罚金备注')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'course_report_fine'


class VirtualclassException(models.Model):

    STUDENT_ABSENCE = VirtualclassInfo.STUDENT_ABSENCE  # 学生缺席
    TEACHER_ABSENCE = VirtualclassInfo.TUTOR_ABSENCE  # 老师缺席
    TEACHER_AND_STUDENT_ABSENCE = VirtualclassInfo.CLASS_NOONE  # 学生老师都缺席

    REASON_CHOICE = (
        (STUDENT_ABSENCE, '学生缺席'),
        (TEACHER_ABSENCE, '老师缺席'),
        (TEACHER_AND_STUDENT_ABSENCE, '学生老师都缺席'),
    )

    virtual_class_id = models.BigIntegerField(verbose_name='virtualclass_id')
    result = models.SmallIntegerField(choices=REASON_CHOICE)
    description = models.CharField(max_length=250, null=True, blank=True)
    cms_user = models.ForeignKey(UserInfo, on_delete=models.DO_NOTHING, db_column='cms_user_id')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manager_virtualclass_exception'
