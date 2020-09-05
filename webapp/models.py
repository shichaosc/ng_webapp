from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from webapp import app_settings
from django.conf import settings
import uuid
from django.utils.translation import ugettext_lazy as _
import logging
import pytz
from datetime import datetime, timedelta
from functools import cmp_to_key
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.db.models.fields.related import ForeignKey

from django.utils.timezone import localtime

from webapp import utils
import json
from .exceptions import OccurrenceDoesNotExist, MultipleEventReturned, MultipleSubscriptionReturned



logger = logging.getLogger(__name__)


class Programme(models.Model):
    """
    Model: The subject of learning

    Description:
        There could be more than one programme - subject. student can choose one as default programme at same time;
        it is allowed to switch from one programme to another programme.

    Attributes:
        programme_name (Str): name of a programme, such as "advanced Mandarin", "Basic Mandarin", etc
        created_on (DateTime)
        updated_on (DateTime)
    """
    programme_name = models.CharField(max_length=50)
    description = models.CharField(max_length=4096)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.programme_name

    class Meta:
        db_table = 'course_programme'


class Course(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    course_level = models.IntegerField()
    course_name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}:{}'.format(self.programme, self.course_name)

    class Meta:
        db_table = 'course_course'


class ClassType(models.Model):
    """
    typename：小班课 smallclass
              一对一 oneonone
    """
    ONE2ONE = 1
    SMALLCLASS = 2

    type_name = models.CharField(max_length=50)
    description = models.CharField(max_length=4096)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s" % (
            self.type_name,
            self.description,
        )

    class Meta:
        db_table = 'student_classtype'


class Tutor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_of_teaching = models.DateField()

    nationality = models.CharField(max_length=2, choices=settings.COUNTRY_CHOICES)
    country_of_residence = models.CharField(max_length=2, choices=settings.COUNTRY_CHOICES)
    rating_PK = models.FloatField(default=4.0)
    rating_ID = models.FloatField(default=4.0)
    rating_LE = models.FloatField(default=4.0)
    rating_OT = models.FloatField(default=4.0)
    rating = models.FloatField(default=3.0)
    total_number_of_classes = models.IntegerField(default=0)
    description = models.CharField(max_length=512)
    # teaching_style = models.CharField(_("teaching_style"), max_length=30, default='')
    description_zhhans = models.CharField(max_length=512, default='')
    is_activate = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    course = models.ManyToManyField(Course, related_name='course')
    class_type = models.ManyToManyField(ClassType, related_name='class_type')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'tutor_tutor'


class AccountBalance(models.Model):
    user = models.ForeignKey(User, related_name='balance', on_delete=models.CASCADE)
    balance = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_accountbalance'

    def __str__(self):
        return self.user.username


class AccountBalanceChange(models.Model):
    NO_REASON = 0
    AD_HOC = 1  # 上课
    PACKAGE = 2
    TOP_UP = 3  # 充值
    BONUS = 4  # 充值奖励
    REFERRAL = 5  # 推荐奖励课时, referrer receives, while referee tops up
    FREE_TRIAL = 6  # 免费试课

    DELIVERY = 7  # 老师讲的课
    INCENTIVE = 8  # 奖励课时
    WITHDRAW = 9  # 提现(老师工资)
    TRANSFER_IN = 10  # 转入
    TRANSFER_OUT = 11  # 转出
    COMPENSATION = 12  # 补偿
    ABSENCE_PENALTY = 13  # penalty for own absence  学生缺席罚金
    NO_SHOW_COMPENSATION = 14  # compensation for tutor's no-show  导师不出席对学生的补偿
    REFUND = 15
    REDEEM = 16  # redeem
    REFERRAL_TRIAL = 17  # referrer receives, while referee takes trial class
    REFERRAL_INCENTIVE = 18  # referee receives, while himself/herself top-up
    TRIAL_CLASS = 112  # Tutor's Free class  家教免费课
    ABSENCE_COMPENSATION = 113  # Compensation for student's absence  学生缺席老师奖励
    NO_SHOW_PENALTY = 114  # penalty for own no-show 对自己不表演的惩罚

    REASON_CHOICES = (
        (NO_REASON, ('NO_REASON')),
        (AD_HOC, ('AD_HOC')),
        (PACKAGE, ('PACKAGE')),
        (TOP_UP, ('TOP_UP')),
        (BONUS, ('TOP UP BONUS')),
        (REFERRAL, ('REFERRAL BONUS')),
        (REFERRAL_INCENTIVE, ('REFERRAL INCENTIVE')),
        (REFERRAL_TRIAL, ('REFERRAL TRIAL')),
        (FREE_TRIAL, ('FREE TRIAL')),
        (COMPENSATION, ('COMPENSATION')),
        (ABSENCE_PENALTY, ('ABSENCE_PENALTY')),
        (NO_SHOW_COMPENSATION, ('NO_SHOW_COMPENSATION')),
        (REFUND, ('REFUND')),
        (DELIVERY, ('COURSE DELIVERY')),
        (INCENTIVE, ('DELIVERY INCENTIVE')),
        (WITHDRAW, ('WITHDRAW')),
        (TRANSFER_IN, ('TRANSFER_IN')),
        (TRANSFER_OUT, ('TRANSFER_OUT')),
        (TRIAL_CLASS, ('TRIAL_CLASS')),
        (ABSENCE_COMPENSATION, ('ABSENCE_COMPENSATION')),
        (NO_SHOW_PENALTY, ('NO_SHOW_PENALTY')),
        (REDEEM, ('REDEEM')),
    )

    user = models.ForeignKey(User, related_name='balance_changes', on_delete=models.CASCADE)
    reason = models.IntegerField(choices=REASON_CHOICES)
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    reference = models.CharField(max_length=1024)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_accountbalancechange'

    def __str__(self):
        return self.user.username


class Transfer(models.Model):
    transfer_user = models.ForeignKey(User, related_name='transfer', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient', on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=6)

    class Meta:
        db_table = 'accounts_transfer'
    def __str__(self):
        return '{} -> {}: {}'.format(self.transfer_user, self.recipient, self.amount)


class Coupon(models.Model):
    code = models.CharField(max_length=50,
                            unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    active = models.BooleanField()


    class Meta:
        db_table = 'accounts_coupon'

    def __str__(self):
        return self.code


class Redeem(models.Model):
    code = models.CharField(max_length=50,
                            unique=True)
    user = models.ForeignKey(User, related_name='Redeem', on_delete=models.CASCADE, blank=True, null=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    active = models.BooleanField()


    class Meta:
        db_table = 'accounts_redeem'

    def __str__(self):
        return self.code


class Price(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_price'

    def __str__(self):
        return self.programme.programme_name


class Package(models.Model):

    duration = models.IntegerField(default=0)
    type_of_duration = models.CharField(choices=app_settings.DURATION_CHOICES, max_length=5)
    limits = models.IntegerField(default=0)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=18, decimal_places=6)

    class Meta:
        db_table = 'accounts_package'

    def __str__(self):
        return '{} {}: {} {}'.format(self.programme, self.class_type, self.duration, self.type_of_duration)


class SalesOrder(models.Model):
    PENDING = 'PENDING'
    PAID = 'PAID'
    CANCELLED = 'CANCELLED'
    REFUNDED = 'REFUNDED'
    STATUS_CHOICES = (
        (PENDING, ('Pending')),
        (PAID, ('Paid')),
        (CANCELLED, ('Canceled')),
        (REFUNDED, ('Refunded')),
    )
    order_no = models.CharField(max_length=36, blank=True, unique=True, default=uuid.uuid4)
    buyer = models.ForeignKey(User, related_name='sales_orders', on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    currency = models.CharField(choices=settings.CURRENCY_CHOICES, max_length=3)
    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               null=True,
                               blank=True, on_delete=models.CASCADE)
    point = models.IntegerField(default=0)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=PENDING)
    reference = models.CharField(max_length=256)
    charge_id = models.CharField(max_length=220, null=True, blank=True)
    source_id = models.CharField(max_length=220, null=True, blank=True)
    remark = models.CharField(max_length=500, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_salesorder'

    def __str__(self):
        return self.buyer.username


class Withdrawal(models.Model):
    class Meta:
        permissions = (
            ("can_review_withdrawal", "Can review withdrawal"),
        )

    SUBMITTED = 'SUBMITTED'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PAID = 'PAID'

    STATUS_CHOICES = (
        (SUBMITTED, ('Submitted')),
        (PAID, ('Paid')),
        (APPROVED, ('Canceled')),
        (REJECTED, ('Rejected')),
    )
    order_no = models.CharField(max_length=36, blank=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, related_name='withdrawal_requester', on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    currency = models.CharField(choices=settings.CURRENCY_CHOICES, max_length=3)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=SUBMITTED)
    reference = models.CharField(max_length=256, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    default_currency = settings.CNY

    class Meta:
        db_table = 'accounts_withdrawal'

    def __str__(self):
        return self.user.username


class ExchangeRate(models.Model):
    currency = models.CharField(choices=settings.CURRENCY_CHOICES, max_length=3)
    rate = models.DecimalField(default=0, max_digits=18, decimal_places=6)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_exchangerate'

    def __str__(self):
        return self.currency


class Subscription(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    remaining_limits = models.IntegerField(default=0)
    reference = models.CharField(max_length=1024)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'accounts_subscription'

    def __str__(self):
        return '{}: {} from {} to {}'.format(self.user, self.remaining_limits, self.start_time, self.end_time)


class SubscriptionUsage(models.Model):
    user = models.ForeignKey(User, related_name='usages', on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    reference = models.CharField(max_length=1024)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'accounts_subscriptionusage'


class Ambassador(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    wechat = models.CharField(max_length=32, null=True, blank=True)
    whatsapp = models.CharField(max_length=32, null=True, blank=True)
    country_calling_code = models.CharField(max_length=3, null=True, blank=True)
    telephone_no = models.CharField(max_length=16, null=True, blank=True)
    occupation = models.CharField(max_length=32, null=True, blank=True)

    GENDER_CHOICES = (
        ('Male', ('Male')),
        ('Female', ('Female')),
        ('N/A', ('N/A')),
    )
    gender = models.CharField(_("gender"), max_length=6, choices=GENDER_CHOICES, null=True,
                              blank=True)  # Male：男； Female：女
    birthdate = models.DateField(_("birthdate"), blank=True, null=True)
    country_of_residence = models.CharField(_("country_of_residence"), max_length=2, choices=settings.COUNTRY_CHOICES, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ambassador_ambassador'

    def __str__(self):
        return 'first_name {} last_name {} wechat {} whatsapp {} telephone_code {} telephone_no {} occupation {}  gender {} birthdate {} country_of_residence {}'.format(self.first_name, self.last_name, self.wechat, self.whatsapp, self.country_calling_code, self.telephone_no, self.occupation, self.gender, self.birthdate, self.country_of_residence)


class Grade(models.Model):

    FIRST_LEVEL = 1
    SECOND_LEVEL = 2
    THREE_LEVEL = 3
    SUPER_LEVEL = 0

    GRADE_CHOICE = (
        (FIRST_LEVEL, 'first level'),
        (SECOND_LEVEL, 'second level'),
        (THREE_LEVEL, 'three level'),
    )

    grade = models.SmallIntegerField(choices=GRADE_CHOICE)
    description = models.CharField(max_length=255, verbose_name='老师等级描述', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tutor_grade'

    def __str__(self):
        return self.get_grade_display()



class BusinessRule(models.Model):
    TYPE_BASE_PAY = 'BASE_PAY'
    TYPE_INCENTIVE_PAY = 'INCENTIVE_PAY'
    TYPE_TOPUP_BONUS = 'TOPUP_BONUS'
    TYPE_REFERRAL_BONUS = 'REFERRAL_BONUS'
    TYPE_REFERRAL_INCENTIVE = 'REFERRAL_INCENTIVE'
    TYPE_TRAIL_BONUS = 'TRAIL_BONUS'

    RULE_CHOICES = (
        (TYPE_BASE_PAY, 1),
        (TYPE_INCENTIVE_PAY, 2),
        (TYPE_TOPUP_BONUS, 3),
        (TYPE_REFERRAL_BONUS, 5),
        (TYPE_REFERRAL_INCENTIVE, 4),
        (TYPE_TRAIL_BONUS, _('TRIAL_BONUS')),
    )

    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, blank=True, null=True)
    tutor_grade = models.ForeignKey(Grade, on_delete=models.CASCADE, blank=True, null=True)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, blank=True, null=True)
    rule_type = models.CharField(max_length=30, choices=RULE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    desc = models.CharField(max_length=256, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_businessrule'


    def __str__(self):
        if self.tutor_grade:
            return '{} for {} - {} - {} & {} ({} - {})'.format(self.rule_type, self.programme, self.class_type,
                                                               self.tutor_grade.get_grade_display(), self.desc,
                                                               self.start_time, self.end_time)
        return '{} for {} - {} & {} ({} - {})'.format(self.rule_type, self.programme, self.class_type, self.desc,
                                                      self.start_time, self.end_time)

class RuleFormula(models.Model):
    rule = models.ForeignKey(BusinessRule, on_delete=models.CASCADE)
    min_amount = models.IntegerField(default=0)
    max_amount = models.IntegerField(default=0)
    amount = models.FloatField(default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_ruleformula'
    def __str__(self):
        return '{} : {} - {}'.format(self.rule, self.min_amount, self.max_amount)


class SocialUser(models.Model):
    STATUS_CHOICES = (
        (0, ''),
        (1, 'checkin'),
        (2, 'signup'),
        (3, 'paid'),
    )
    app = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE,)
    openid = models.CharField(max_length=100, default='')
    app_username = models.CharField(max_length=100, default='')
    app_avatar = models.CharField(max_length=1000, blank=True)
    app_referrer = models.ForeignKey(User, related_name='appreferrer', on_delete=models.CASCADE, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    account_balance = models.ForeignKey(AccountBalance, null=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_referrer = models.BooleanField(default=False)
    is_referree = models.BooleanField(default=False)
    phone_num = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'campaign_socialuser'

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return '{}'.format(self.app_username)


class Session(models.Model):
    Active = 'Active'
    Archived = 'Archived'
    STATUS_CHOICES = (
        (Active, 'Active'),
        (Archived, 'Archived')
    )
    course =models.ForeignKey(Course, on_delete=models.CASCADE)
    session_no = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=Active)

    def _get_session_name(self):
        # course_name = Course.objects.get(id=self.course.id).course_name
        # return '%s - lesson %s' % (course_name, self.session_no)
        return 'lesson {0}'.format(self.session_no)

    session_name = property(_get_session_name)
    class Meta:
        db_table = 'course_session'

    def __str__(self):
        return '{}:{}({})'.format(self.course, self.session_name, self.status)


class Courseware(models.Model):
    session =models.ForeignKey(Session, on_delete=models.CASCADE)
    cw_type = models.CharField(max_length=20, choices=(('ppt', 'ppt'), ('image', 'image'), ('pdf', 'pdf')),
                               default='image')
    cw_seq = models.IntegerField()
    # cw_content = models.FileField(upload_to='cw/%Y/%m')
    cw_content = models.CharField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_courseware'


    def __str__(self):
        return self.session


class SessionTkFile(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    tk_file_id = models.CharField(max_length=30, blank=True, null=True, )
    class Meta:
        db_table = 'course_sessiontkfile'
    def __str__(self):
        return '{}   {}'.format(self.session, self.tk_file_id)


class CourseTest(models.Model):
    course =models.ForeignKey(Course, on_delete=models.CASCADE)
    test_content = models.FileField(upload_to='exambank/')
    test_prefix = models.CharField(max_length=2)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_coursetest'

    def __str__(self):
        return self.course.course_name


class TestResult(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    course =models.ForeignKey(Course, on_delete=models.CASCADE)
    test_level = models.FloatField(default=1.0)
    question_no = models.IntegerField()
    correct_answer_no = models.IntegerField()
    score = models.IntegerField()
    detail = models.CharField(max_length=4096)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_testresult'
    # def __str__(self):
    # return '{0} - {1}'.format(self.user.username, self.course.course_level)


class AssessmentResult(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    course =models.ForeignKey(Course, on_delete=models.CASCADE)
    detail = models.CharField(max_length=4096)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_assessmentresult'


    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.course.programme.programme_name)


class TestQuestion(models.Model):
    question_id = models.CharField(max_length=16)
    course =models.ForeignKey(Course, on_delete=models.CASCADE)
    Single_Choice = 'Single_Choice'
    Multiple_Choice = 'Multiple_Choice'
    Drag_Drop = 'Drag_Drop'
    TYPE_CHOICES = (
        (Single_Choice, 'Single Choice'),
        (Multiple_Choice, 'Multiple Choice'),
        (Drag_Drop, 'Drag & Drop'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=20, default=Single_Choice)
    Active = 'Active'
    Archived = 'Archived'
    IS_ACTIVE = (
        (Active, 'Active'),
        (Archived, 'Archived')
    )
    status = models.CharField(choices=IS_ACTIVE, max_length=10, default=Active)
    degree_of_difficulty = models.FloatField(default=0.0)
    detail = models.CharField(max_length=4096)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_testquestion'

    def __str__(self):
        return '{}---{}'.format(self.course.course_name, self.question_id)


class CourseManager(models.Manager):
    """
    Manager: The subject of learning

    TODO: move create_usercourse to Course APP
    """

    def is_user_assessed(self, user):
        user_course = UserCourse.objects.get_default_usercourse(user=user)
        return user_course.is_assessed


class UserCourse(models.Model):
    """
    Model: The subject of learning

    Description:
        There could be more than one programme - subject. student can choose one as default programme at same time;
        it is allowed to switch from one programme to another programme.

    Attributes:
        programme_name (Str): name of a programme, such as "advanced Mandarin", "Basic Mandarin", etc
        created_on (DateTime)
        updated_on (DateTime)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    is_assessed = models.BooleanField(default=False)
    session_no = models.IntegerField(default=0)
    test_level = models.FloatField(default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_usercourse'
    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.course.programme.programme_name)


class Homework(models.Model):
    """
    Model: The original content of homework, to be finished by student.


    """
    session =models.ForeignKey(Session, on_delete=models.CASCADE)
    hw_content = models.CharField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,
                              choices=(('finished', 'finished'), ('assessed', 'assessed'), ('None', 'None')),
                              default='None')

    class Meta:
        db_table = 'course_homework'

    def __str__(self):
        return '{0} - {1}'.format(self.session.course, self.session)


class HomeworkResult(models.Model):
    """
    Model: The assessment result of homework, which is finished by student
    """
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    homework =models.ForeignKey(Homework, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    comment = models.TextField(default=None, blank=True, null=True)

    class Meta:
        db_table = 'course_homeworkresult'

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.id, self.user_id, self.homework_id)


class Donehomework(models.Model):
    """
    Model: The uploaded homework, which is already finished by student
    """
    homeresult =models.ForeignKey(HomeworkResult, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    result_content = models.CharField(max_length=1000)

    class Meta:
        db_table = 'course_donehomework'


class TeachPlan(models.Model):
    session =models.ForeignKey(Session, on_delete=models.CASCADE)
    tp_content = models.CharField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_teachplan'

    def __str__(self):
        return '{0} - {1}'.format(self.session.course, self.session)


class ExtCourseTag(models.Model):

    text = models.TextField(default='', null=True, blank=True, verbose_name='标签')
    ext_course_type = models.CharField(max_length=20, choices=(('Option', 2), ('Required', 1)),
                                       default='Option')

    class Meta:
        db_table = 'course_extcoursetag'

class ExtCourseManager(models.Manager):
    def get_fresh_extcourse_by_user_course_and_session_id(self, usercourse_id, session_id):
        ext_user_course = ExtUserCourse.objects.filter(user_course_id=usercourse_id, session_id=session_id).first()
        if ext_user_course:
            ext_course = ExtCourse.objects.get(id=ext_user_course.ext_course.id)
            if ext_course.ext_course_id:
                ext_course = ExtCourse.objects.get(ext_course_id=ext_course.ext_course_id,
                                                   ext_course_active=ExtCourse.Active)
            return ext_course


class ExtCourse(models.Model):
    Public = 'Public'
    Private = 'Private'
    STATUS_CHOICES = (
        (Public, 2),
        (Private, 1)
    )

    Active = 'Active'
    Archived = 'Archived'
    IS_ACTIVE = (
        (Active, 1),
        (Archived, 2)
    )



    ext_course_name = models.CharField(max_length=50)
    ext_course_tag = models.ForeignKey(ExtCourseTag, on_delete=models.CASCADE)
    ext_course_type = models.CharField(max_length=20, choices=(('old', 1), ('new', 2)), default='old')
    ext_course_status = models.CharField(choices=STATUS_CHOICES, max_length=10, default=Public)
    ext_course_active = models.CharField(choices=IS_ACTIVE, max_length=10, default=Active)
    ext_course_id = models.IntegerField(default=0)
    tk_ext_id = models.CharField(max_length=30, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    objects = ExtCourseManager()

    class Meta:
        db_table = 'course_extcourse'

    @property
    def res_op_tag_list(self):
        op_tag_list = []
        try:
            op_tag_list = [obj.ext_course_op_tag.text for obj in self.extcourseoptag_set.all()]
        except Exception:
            op_tag_list = []
        return op_tag_list

    @property
    def res_ext_course_cover(self):
        course_cover_url = ''
        try:
            course_cover_url = self.extcourseware_set.filter(ecw_type='image').first().ecw_content.url
        except Exception:
            course_cover_url = ''
        return course_cover_url


class ExtCourseOpTag(models.Model):
    ext_course =models.ForeignKey(ExtCourse, on_delete=models.CASCADE)
    ext_course_op_tag = models.ForeignKey(ExtCourseTag, on_delete=models.CASCADE)

    class Meta:
        db_table = 'course_extcourseoptag'

class ExtCourseware(models.Model):
    ext_course =models.ForeignKey(ExtCourse, on_delete=models.CASCADE)
    ecw_type = models.CharField(max_length=20, choices=(('ppt', 1), ('image', 2), ('pdf', 3)),
                                default='image')
    ecw_seq = models.IntegerField()
    ecw_content = models.CharField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'course_extcourseware'


class ExtCourseOwner(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    ext_course =models.ForeignKey(ExtCourse, on_delete=models.CASCADE)
    is_favorite = models.IntegerField(default=0, verbose_name="是否收藏")

    class Meta:
        db_table = 'course_extcourseowner'


class ParentQuestionnaire(models.Model):
    no_id = models.IntegerField(default=0)
    tittle = models.CharField(max_length=256)
    tittle_en = models.CharField(max_length=256)
    Active = 'Active'
    Archived = 'Archived'
    IS_ACTIVE = (
        (Active, 1),
        (Archived, 0)
    )
    status = models.CharField(choices=IS_ACTIVE, max_length=10, default=Active)
    detail = models.CharField(max_length=4096)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_parentquestionnaire'

    def __str__(self):
        return 'no_id {} detail {}'.format(self.no_id, self.detail)


class ExtUserCourseManager(models.Manager):

    def record_extcw(self, user_id, session_id):
        usecourse_id = UserCourse.objects.get_default_usercourse(User.objects.get(id=user_id))
        ext_course = ExtCourse.objects.get_fresh_extcourse_by_user_course_and_session_id(usecourse_id, session_id)
        extusercouse = ExtUserCourse.objects.get(user_course_id=usecourse_id, session_id=session_id)
        extusercouse.confirm_id = ext_course.id
        extusercouse.save()


class ExtUserCourse(models.Model):
    user_course =models.ForeignKey(UserCourse, on_delete=models.CASCADE)
    session =models.ForeignKey(Session, on_delete=models.CASCADE)
    ext_course =models.ForeignKey(ExtCourse, on_delete=models.CASCADE)
    confirm_id = models.IntegerField(null=True)
    objects = ExtUserCourseManager()
    class Meta:
        db_table = 'course_extusercourse'


class QuestionnaireResult(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.CharField(max_length=2000)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'course_questionnaireresult'


class LearningGroup(models.Model):
    virtual_class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE)
    members = models.ManyToManyField(
        User,
        through='Membership',
        through_fields=('learning_group', 'group_member'),
    )

    OPEN = 1
    CLOSED = 0
    STATUS_TYPE_CHOICES = (
        (OPEN, 'OPEN'),
        (CLOSED, 'CLOSED'),
    )
    status = models.CharField(choices=STATUS_TYPE_CHOICES, max_length=20, default=OPEN)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=4096, null=True, blank=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'student_learninggroup'

    def __str__(self):
        return "%s %s (%s)" % (
            self.id,
            self.virtual_class_type,
            ",members ".join(member.username for member in self.members.all())
        )



class MemberItem(object):

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    def __str__(self):
        return "%s %s" % (
            self.user_id,
            self.username
        )


class SmallClassListItem(object):

    def __init__(self, group_id, monitor_id, monitor_avatar, course_id, course_name,course_level, session_no, member_item_list, description, monitor_name):
        self.group_id = group_id
        self.monitor_id = monitor_id
        self.monitor_avatar = monitor_avatar
        self.course_id = course_id
        self.course_name = course_name
        self.course_level = course_level
        self.session_no = session_no
        self.member_list = member_item_list
        self.description = description
        self.monitor_name = monitor_name

    def __str__(self):
        return "grouo_d:%s  %s  monitor_id:%s %s course_id:%s session_no%s %s (%s)" % (
            self.group_id,
            self.monitor_id,
            self.monitor_avatar,
            self.course_id,
            self.course_name,
            self.session_no,
            self.monitor_name,
            ",members ".join(member.username for member in self.member_list)
        )

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class MonitorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Membership.Monitor)


class MemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Membership.Member)

class AllMembersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(role=Membership.Member) | Q(role=Membership.Monitor))


class Membership(models.Model):
    learning_group = models.ForeignKey(LearningGroup, on_delete=models.CASCADE)
    group_member = models.ForeignKey(User, on_delete=models.CASCADE)
    Monitor = 1
    Member = 2
    ROLE_TYPE_CHOICES = (
        (Monitor, 'Monitor'),
        (Member, 'Member'),
    )
    role = models.CharField(choices=ROLE_TYPE_CHOICES, max_length=20, default=Monitor)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # monitors = MonitorManager()
    # members = MemberManager()
    # all_members = AllMembersManager()


    class Meta:
        db_table = 'student_membership'

    def __str__(self):
        return "%s %s %s" % (
            self.id,
            self.learning_group,
            self.role
        )


class GroupOperatingRecord(models.Model):
    learning_group = models.ForeignKey(LearningGroup, on_delete=models.CASCADE)
    group_member = models.ForeignKey(User, on_delete=models.CASCADE)
    Monitor = 1
    Member = 2
    ROLE_TYPE_CHOICES = (
        (Monitor, 'Monitor'),
        (Member, 'Member'),
    )
    STATUS_IN = 1
    STATUS_OUT = 2
    STATUS_CHOICES = (
        (STATUS_IN, 'In'),
        (STATUS_OUT, 'Out'),
    )
    role = models.CharField(choices=ROLE_TYPE_CHOICES, max_length=20, default=Monitor)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=STATUS_IN)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)



    class Meta:
        db_table = 'student_groupoperatingrecord'




class EventManager(models.Manager):
    """
    manage the basic functions of event manipulation, including create, update, delete, extend
    """

    def create_event(self, user, start, end, end_recurring_period, **extra_fields):
        """
        TODO: need check whether event is conflict with existing events
        """

        if self.has_existing_event(user, start, end, end_recurring_period):
            return False, None

        one_week_ago = start - timedelta(weeks=1)
        existing_event = self.get_event_by_occurrence_start(user, one_week_ago)

        if existing_event:
            logger.debug('extend existing event, instead of creating a new event, and existing event is {}'.format(
                existing_event.id))
            return self.update_event(user, start, end, end_recurring_period, existing_event)
        else:
            event = self.model(user=user, start=start, end=end, end_recurring_period=end_recurring_period,
                               **extra_fields)
            event.save()
            result, sub = EventSubscription.objects.renew_subscription(event, app_settings.LOOK_BACK_BY_WEEK)
            if result:
                logger.debug(
                    'renew subscription, the new subscription {} starts from {} to {}'.format(sub.id, sub.start_time,
                                                                                              sub.end_time))

            return True, event

    def update_event(self, user, start, end, end_recurring_period, event, **extra_fields):
        if not event:
            return False, None

        if end_recurring_period < event.end_recurring_period and event.has_active_subscription(end_recurring_period,
                                                                                               event.end_recurring_period):
            return False, event

        event.end_recurring_period = end_recurring_period
        event.save()

        # if the event does not have any occurrence, it can be deleted
        if event.start == event.end_recurring_period:
            self.delete_event(event)
        # logger.debug('update event {} with end_recurring_period {}'.format(event.id, event.end_recurring_period))

        return True, event

    def create_or_update_event(self, user, start, end, end_recurring_period, event=None, **extra_fields):
        if event:
            return self.update_event(user, start, end, end_recurring_period, event, **extra_fields)
        else:
            return self.create_event(user, start, end, end_recurring_period, **extra_fields)

    def delete_event(self, event):
        """
        Function: delete event

        Description: if there is any subscription, it can't be deleted.

        Args:


        Returns:
        """

        # if there is any subscription, the event could not be deleted
        if event.has_active_subscription(event.start, event.end_recurring_period):
            return False

        event.delete()
        return True

    def cancel_event(self, event, start, cancel_remaining=False):
        """
        Function: delete event

        Description: if there is active EventSubscription or active appointment, the event can't be cancelled.

        Args:


        Returns:
        """

        # if the start doesn't match, throw exception
        occurrence = event.get_occurrence(start)
        if not occurrence:
            raise OccurrenceDoesNotExist('Occurrence with specific start time does not exist')

        if cancel_remaining:
            return self.cancel_remaining_occurrences(event, start)
        else:
            return self.cancel_single_occurrence(event, start)

    def get_event_by_occurrence_start(self, user, start):
        """
        get event by the specific time - occurrence start, such as '2018-01-23 08:00:00 UTC"

        Restriction: At same occurrence time, one user should no more than 1 event
        """
        events = self.filter(user=user, start__lte=start, end_recurring_period__gt=start)

        event = None
        for e in events:
            if e.start >= e.end_recurring_period:
                continue
            occurrence = e.get_occurrence(start)
            if occurrence:
                if not event:
                    event = e
                else:
                    raise MultipleEventReturned('more than one event are found at same time')

        return event

    #todo
    def cancel_single_occurrence(self, event, start):

        end = start + (event.end - event.start)
        if event.has_active_subscription(start, end):
            return False

        one_week_later = start + timedelta(weeks=1)
        original_end_recurring_period = event.end_recurring_period
        # just change event end_recurring_priod to occurrence start
        event.end_recurring_period = start
        event.save()

        if original_end_recurring_period > one_week_later:

            # create a new event start from one week after occurrence's start
            end = one_week_later + (event.end - event.start)
            result, new_event = Event.objects.create_event(event.user, one_week_later, end,
                                                           original_end_recurring_period)

            # create new event subscriptions, if there are any ones related to the event with cancelled occurrence
            subscriptions = EventSubscription.objects.filter(event=event)
            for sub in subscriptions:
                if sub.start_time >= one_week_later:
                    sub.event = new_event
                    sub.save()
        return True

    def cancel_remaining_occurrences(self, event, start):
        end = event.end_recurring_period
        if event.has_active_subscription(start, end):
            return False

        result = self.extend_event_cancellation(event, start, app_settings.LOOK_FORWARD_BY_WEEK)
        if not result:
            return False

        # just change event end_recurring_priod to occurrence start
        event.end_recurring_period = start
        event.save()

        return True

    def extend_event_cancellation(self, event, start, look_forward=0):

        t_current_week = event.start
        while t_current_week < event.end_recurring_period:
            t_current_week = t_current_week + timedelta(weeks=1)

        week = 0
        while week <= look_forward:

            next_event = self.get_event_by_occurrence_start(event.user, t_current_week)

            if next_event:
                result = self.cancel_remaining_occurrences(next_event, t_current_week)
                if not result:
                    return False

            t_current_week = t_current_week + timedelta(weeks=1)
            week += 1

        return True

        # TODO: move this function to OccurrenceManager

    def get_occurrence_list(self, tutor, start, end, student_id=None):

        if isinstance(tutor, int) or isinstance(tutor, str):
            tutor_id = tutor
        else:
            tutor_id = tutor.id

        occurrences = []

        events = Event.objects.filter(user__id=tutor_id, start__lt=end, end_recurring_period__gte=start)
        for event in events:
            logger.debug('event item: {0}'.format(event))
            occurrences_of_e = event.get_occurrence_list(start, end)
            occurrences.extend(occurrences_of_e)

        all_subscriptions = EventSubscription.objects.filter(end_time__gt=start, event__user__id=tutor_id)

        subscription_occurrence_list = []

        for subscription in all_subscriptions:
            subscription_occurrences = subscription.get_occurrence_list_v2(start, end, student_id)
            subscription_occurrence_list.extend(subscription_occurrences)

        subscription_dict = {}
        for sub_occurrence in subscription_occurrence_list:
            subscription_dict[sub_occurrence.start] = sub_occurrence

        for occurrence in occurrences[::-1]:
            event_start = occurrence.start
            if event_start in subscription_dict.keys():
                occurrences.remove(occurrence)
            else:
                before_event_start = event_start + timedelta(minutes=-30)
                next_event_start = event_start + timedelta(minutes=30)
                if (before_event_start in subscription_dict.keys()) or (next_event_start in subscription_dict.keys()):
                    occurrence.is_occupied = 3
                    occurrence.is_available =False
        subscription_occurrence_list.extend(occurrences)

        return subscription_occurrence_list

    def has_existing_event(self, user, start, end, end_recurring_period):
        logger.debug(
            'check has_existing_event, start is {}; end_recurring_period is {} '.format(start, end_recurring_period))

        events = self.filter(user=user).exclude(start__gte=end_recurring_period).exclude(
            end_recurring_period__lte=start)
        t_start = start.astimezone(pytz.utc)
        for event in events:
            # don't count the zero duration event
            if event.start == event.end_recurring_period:
                continue
            if event.start.weekday() == t_start.weekday() and event.start.hour == t_start.hour and event.start.minute == t_start.minute:
                logger.debug('{} exists'.format(event))
                return True
        return False


class SubscriptionManager(models.Manager):

    def get_subscribed_occurrence_list(self, student, start, end):
        occurrences = []

        event_subscriptions = self.filter(sub_invitees__in=student, start_time__lt=end, end_time__gte=start).order_by("start_time")
        for es in event_subscriptions:

            occurrences_of_e = es.get_occurrence_list(start, end)
            for o in occurrences_of_e:
                if o.start >= es.start_time and o.start < es.end_time:
                    occurrences.append(o)

        skey = cmp_to_key(lambda x, y: y.start.timestamp() - x.start.timestamp())
        occurrences.sort(key=skey)

        return occurrences

    def get_subscribed_occurrence_list_by_tutor(self, tutor, start, end):
        occurrences = []

        event_subscriptions = self.filter(event__user=tutor, start_time__lt=end, end_time__gte=start).order_by("start_time")
        for es in event_subscriptions:
            occurrences_of_e = es.get_occurrence_list(start, end)
            for o in occurrences_of_e:
                if o.start >= es.start_time and o.start < es.end_time:
                    occurrences.append(o)

        skey = cmp_to_key(lambda x, y: y.start.timestamp() - x.start.timestamp())
        occurrences.sort(key=skey)

        return occurrences


    def get_subscription_by_occurrence_start(self, users, start, user):
        """
        get event subscription by the specific time - occurrence start, such as '2018-01-23 08:00:00 UTC"

        Restriction: At same occurrence time, one user should no more than 1 event subscription
        """
        users = []
        # for u in user:
        #     users.append(u.id)
        subscriptions = self.filter(
            sub_invitees=user,
            start_time__lte=start,
            end_time__gt=start,
            event__start__lte=start,
            event__end_recurring_period__gt=start)

        sub = None
        for s in subscriptions:
            occurrence = s.event.get_occurrence(start)
            if occurrence:
                if not sub:
                    sub = s
                else:
                    raise MultipleSubscriptionReturned('more than one event subscription are found at same time')

        return sub

    def create_event_subscription(self, event, invitee, start, end, group_id=None, generating_appointment=False):
        class_end = start + timedelta(minutes=Event.default_event_duration)
        members = LearningGroup.objects.get_class_members_by_id(group_id)
        learning_group = LearningGroup.objects.get_learning_group_by_id(group_id=group_id)
        """ TODO: add conflict check """
        sub = EventSubscription(event=event,
                                start_time=start,
                                end_time=end,
                                learning_group=learning_group
                                )
        sub.save()
        if members:
            for invitee in members:
                sub.sub_invitees.add(invitee)
            sub.save()

        if sub.end_time > event.end_recurring_period:
            ret, new_sub = self.extend_subscription(sub, app_settings.LOOK_FORWARD_BY_WEEK, group_id)
            if ret:
                logger.info('subscription {} is extended with new subscription {}'.format(sub, new_sub))

        # if generating_appointment:
        if generating_appointment:
            if event.start <= sub.start_time \
                    and event.start < event.end_recurring_period \
                    and sub.start_time < event.end_recurring_period:  # 预占或者event取消不生成appointment
                appointment = Appointment.objects.create_appointment(sub,
                                                                     start,
                                                                     class_end)

        return True, sub

    def get_unconfirmed_occurrence_list(self, student, start, end):

        occurrences = self.get_subscribed_occurrence_list(student, start, end)

        for o in occurrences:
            app = Appointment.objects.filter(invitees__in=student, event_subscription__id=o.subscription_id,
                                             original_start=o.start).first()

            if app:
                occurrences.remove(o)
                logger.debug('occurrence is removed: {}'.format(o))

        return occurrences

    def get_unconfirmed_occurrence_list_by_totur(self, tutor, start, end):

        occurrences = self.get_subscribed_occurrence_list_by_tutor(tutor, start, end)

        for o in occurrences:
            app = Appointment.objects.filter(event_subscription__event__user=tutor, event_subscription__id=o.subscription_id,
                                             original_start=o.start).first()

            if app:
                occurrences.remove(o)
                logger.debug('occurrence is removed: {}'.format(o))

        return occurrences

    def cancel_subscription(self, event_subscription, start, cancel_remaining=False, user=None, is_occupied='0'):
        if cancel_remaining:  # 多次取消
             return self.cancel_remaining_occurrences(event_subscription, start, user)
        else:
            if is_occupied == '1':
                return self.cancel_single_occurrence_occupy(event_subscription, start)
            else:
                return self.cancel_single_occurrence(event_subscription, start)

    def cancel_virturl_sub(self, event_subscription, start):

        end = start + timedelta(minutes=45)
        app = Appointment.objects.create_appointment(event_subscription, start, end, True)
        app.cancel(mute=True)

        return True

    def cancel_single_occurrence(self, event_subscription, start):

        occurrence = event_subscription.get_occurrence(start)

        if not occurrence:
            raise OccurrenceDoesNotExist('Occurrence with specific start time does not exist')

        appointments = Appointment.objects.get_appointments_by_occurrence(occurrence)
        if appointments.count() > 0:
            for app in appointments:
                if app.status == Appointment.CONFIRMED:
                    app.cancel()
        else:
            end = start + (event_subscription.event.end - event_subscription.event.start)
            app = Appointment.objects.create_appointment(event_subscription, start, end, True)
            app.cancel(mute=True)

        return True, event_subscription

    def cancel_single_occurrence_occupy(self, event_subscription, start):

        end = start + (event_subscription.event.end - event_subscription.event.start)
        app = Appointment.objects.create_appointment(event_subscription, start, end, True)
        app.cancel(mute=True)

        return True, event_subscription

    def cancel_remaining_occurrences(self, event_subscription, start, user=None):
        # if event_subscription.start_time == start:
        #     event_subscription.delete()
        #     return True, event_subscription
        occurrences = event_subscription.get_occurrence_list(start, event_subscription.end_time)
        re_start = start
        # update event subscription end time to the moment, at which user would cancel all the remaining
        event_subscription.update_end_time(re_start)
        result = self.extend_subscription_cancellation(event_subscription, app_settings.LOOK_FORWARD_BY_WEEK, user)
        for o in occurrences:
            appointments = Appointment.objects.get_appointments_by_occurrence(o)
            for app in appointments:
                app.delete()
        logger.debug('cancel remaining subscription {}'.format(event_subscription))

        return True, event_subscription

    def renew_subscription(self, event, look_back=0):
        '''
        Description: if the event has been broken by one or more weeks off, existing subscription could be
        renewed automatically within look-back period (by week)
        '''
        result = None
        new_sub = None
        week = 1
        while week <= look_back:
            t_start = event.start - timedelta(weeks=week)

            previous_event = Event.objects.get_event_by_occurrence_start(event.user, t_start)
            if previous_event is not None:
                subs = EventSubscription.objects.filter(event=previous_event, end_time__gt=event.start)
                new_sub = None
                for sub in subs:
                    if sub.start_time < event.start:
                        # generate new subscription
                        result, new_sub = EventSubscription.objects.create_event_subscription(
                            event, sub.sub_invitees, event.start, sub.end_time, sub.learning_group.id)
                        # update appointment and subscription
                        sub.update_end_time(event.start)
                        Appointment.objects.filter(event_subscription=sub, original_start__gte=event.start).update(
                            event_subscription=new_sub)
                    else:
                        sub.update_event(event)

                if new_sub:
                    return True, new_sub

            week += 1

            # 如果向前看两周没有预占，有可能出现的一种情况是在当周预占过又取消了，然后老师又发布了课程
            if week == look_back + 1:
                result, new_sub = EventSubscription.objects.renew_subscription_preempted(event, look_back=0)
        if result:
            return True, new_sub
        return False, None

    def renew_subscription_preempted(self, event, look_back=0):
        '''
        Description: 在这个上课时间段，如果之前存在过event，且被学生预占过，当创建event的时候，需要更新预占的event_sub
        '''
        # timezone.utc
        event_utc_start = localtime(event.start, timezone=timezone.utc)
        subs = EventSubscription.objects.filter(event__user=event.user).exclude(
            Q(start_time__gt=event.end_recurring_period) | Q(end_time__lt=event.start))
        preempting_subs = []
        for sub in subs:
            if sub.start_time.weekday() == event_utc_start.weekday() and sub.start_time.hour == event_utc_start.hour and sub.start_time.minute == event_utc_start.minute:
                preempting_subs.append(sub)

        for preempt in preempting_subs[::-1]:
            sub_start = preempt.start_time
            sub_end = preempt.end_time
            cancel_sub = True
            while sub_start < sub_end:
                appointment = Appointment.objects.filter(scheduled_time=sub_start, event_subscription=preempt).first()
                if not appointment or appointment.status == Appointment.CONFIRMED:
                    cancel_sub = False
                    break
                sub_start = sub_start + timedelta(weeks=1)

            if cancel_sub:
                preempting_subs.remove(preempt)

        if len(preempting_subs) == 1:
            if (event.start - preempting_subs[0].event.start).days <= 7 * (look_back + 1):
                preempting_subs[0].event = event
                preempting_subs[0].save()
                logger.debug('The event {} has been preempted ,the preempting subscription  is {}'.format(event,
                                                                                                          preempting_subs[
                                                                                                              0]))
                return True, preempting_subs[0]

        if len(preempting_subs) > 1:
            logger.debug(
                'The event {} has been preempted ,but the preempting subscriptions  more than one, it is wrong!'.format(
                    event))
            return False, None
        return False, None

    def extend_subscription(self, event_subscription, look_forward=0, group_id=None):

        t_current_week = event_subscription.event.start
        while t_current_week < event_subscription.event.end_recurring_period:
            t_current_week = t_current_week + timedelta(weeks=1)

        week = 0
        while week <= look_forward:
            next_event = Event.objects.get_event_by_occurrence_start(event_subscription.event.user, t_current_week)
            if next_event:
                result, new_sub = self.create_event_subscription(next_event, event_subscription.sub_invitees, t_current_week,
                                                                 event_subscription.end_time, group_id)
                event_subscription.update_end_time(t_current_week)
                return True, new_sub
            t_current_week = t_current_week + timedelta(weeks=1)
            week += 1
        return False, None

    def extend_subscription_cancellation(self, event_subscription, look_forward=0, user=None):
        t_current_week = event_subscription.event.start
        while t_current_week < event_subscription.event.end_recurring_period:
            t_current_week = t_current_week + timedelta(weeks=1)

        week = 0
        while week <= look_forward:
            next_sub = self.get_subscription_by_occurrence_start(event_subscription.sub_invitees.all(), t_current_week, user)

            if next_sub:
                self.cancel_remaining_occurrences(next_sub, t_current_week)

            t_current_week = t_current_week + timedelta(weeks=1)
            week += 1

    def remove_smallclass_member_from_eventsubscription(self, user, learning_group):
        t_now = timezone.now()
        event_subscriptions = self.filter(learning_group_id=learning_group.id).all()
        for es in event_subscriptions:
            EventSubscription.objects.remove_user_from_eventsubscription(user, es)

        return event_subscriptions

    def montor_remove_smallclass_member_from_eventsubscription(self, user, learning_group):
        # t_now = timezone.now()
        # appointments = Appointment.objects.filter(status=Appointment.CONFIRMED,
        #                                           original_start__gte=t_now,
        #                                           learning_group=learning_group).all()
        # es_list = []
        # for appointment in appointments:
        #     if hasattr(appointment, 'event_subscription'):
        #         es_list.append(appointment.event_subscription.id)
        # event_subscriptions = self.filter(learning_group_id=learning_group.id).exclude(id__in=es_list).all()
        t_now = timezone.now()
        one_week = timedelta(weeks=1)
        event_subscriptions = self.filter(end_time__gte=t_now, learning_group_id=learning_group.id).all()
        for es in event_subscriptions:
            if es.end_time - t_now < one_week:
                self.cancel_subscription(es, es.start_time+one_week, True)
            else:
                self.cancel_subscription(es, t_now, True)


        return event_subscriptions

    def add_smallclass_member_into_eventsubscriptions(self, user, learning_group):
        t_now = timezone.now()
        event_subscriptions = self.filter(start_time__gte=t_now, learning_group=learning_group).all()
        for es in event_subscriptions:
            SubscriptionManager.add_user_into_eventsubscription(user, es)

        return event_subscriptions

    @staticmethod
    def remove_user_from_eventsubscription(user, subscription):
        subscription.sub_invitees.remove(user)
        subscription.save()
        return subscription

    @staticmethod
    def add_user_into_eventsubscription(user, subscription):
        subscription.sub_invitees.add(user)
        subscription.save()
        return subscription


class AppointmentManager(models.Manager):

    def get_appointments_by_occurrence(self, occurrence):
        # logger.debug('subscription id is {}'.format(occurrence.subscription_id))
        sub = EventSubscription.objects.get(id=occurrence.subscription_id)
        return self.get_appointments(sub, occurrence.start)

    def get_appointments(self, event_subscription, start):
        appointments = Appointment.objects.filter(scheduled_time=start, event_subscription=event_subscription)
        return appointments


    def create_appointments(self, user, start, end):
        count = 0

        occurrences = EventSubscription.objects.get_unconfirmed_occurrence_list(user, start, end)

        for o in occurrences:

            subscription = EventSubscription.objects.get(id=o.subscription_id)

            app = Appointment.objects.filter(invitees__in=[user], event_subscription=subscription,
                                             original_start=o.start).first()

            if not app:
                self.create_appointment(subscription, o.start, o.end)

                count += 1

        return count


    @staticmethod
    def is_user_get_one_appointment_confirmed(user):
        try:
            appointment = Appointment.objects.filter(invitees=user, status=Appointment.CONFIRMED).exists()
        except Appointment.DoesNotExist:
            return False
        return appointment


    def remove_smallclass_member_from_appointments(self, user, learning_group):
        t_now = timezone.now()
        appointments = self.filter(status=Appointment.CONFIRMED,
                                   scheduled_time__gte=t_now,
                                   learning_group=learning_group).all()

        for appointment in appointments:
            Appointment.objects.remove_user_from_appointment(user, appointment)

        return appointments


    def smallclass_add_member_into_appointments(self, user, learning_group):
        t_now = timezone.now()
        appointments = self.filter(status=Appointment.CONFIRMED,
                                   original_start__gte=t_now,
                                   learning_group=learning_group).all()

        for appointment in appointments:
            AppointmentManager.add_user_into_appointment(user, appointment)

    @staticmethod
    def remove_user_from_appointment(user, appointment):
        logging.debug("remove user = {} from appointment = {}".format(user, appointment))
        appointment.invitees.remove(user)
        appointment.save()
        return appointment

    @staticmethod
    def add_user_into_appointment(user, appointment):
        appointment.invitees.add(user)
        appointment.save()
        return appointment

    def is_have_appointment_before_class_start_two_hours(self, user):
        t_now = timezone.now()
        two_hours = timedelta(hours=2)
        end_now = t_now + two_hours
        start_now = t_now - two_hours
        logging.debug("t_nowt_nowt_now  = {} end_nowend_now  = {}".format(start_now, end_now))
        is_exsit = self.filter(scheduled_time__range=(start_now, end_now),
                               status=Appointment.CONFIRMED,
                               invitees=user).exists()

        return is_exsit

    def has_appointment_after_two_hours(self, user, learning_group_id):
        t_now = timezone.now()
        two_hours = timedelta(hours=2)
        end_now = t_now + two_hours
        start_now = t_now - two_hours
        logging.debug("t_nowt_nowt_now  = {} end_nowend_now  = {}".format(start_now, end_now))
        is_exsit = self.filter(scheduled_time__range=(start_now, end_now),
                               status=Appointment.CONFIRMED,
                               invitees=user, learning_group__id=learning_group_id).exists()

        return is_exsit



# event object manages available time slots of tutor.
class Event(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField(help_text="The end time must be later than the start time.")
    end_recurring_period = models.DateTimeField(null=True, blank=True,
                                                help_text="This date is ignored for one time only events.")
    maximum_invitee = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    objects = EventManager()

    class Meta:
        db_table = 'scheduler_event'

    def __str__(self):
        return '{}: {} ({} - {})'.format(self.id, self.user.username, self.start, self.end_recurring_period)

    def get_occurrence_list(self, start, end):
        o_start = self.start
        o_end = self.end

        if end > self.end_recurring_period:
            end = self.end_recurring_period

        week = timedelta(weeks=1)
        occurrences = []
        while o_start < end:
            if o_start >= start and o_start < self.end_recurring_period:

                s_start = None
                s_end = None
                s_invitee = None
                s_id = None
                occurrence = Occurrence(self.id, o_start, o_end, self.start, self.end, self.end_recurring_period, None, None,
                                        None, None)
                occurrences.append(occurrence)
            o_start = o_start + week
            o_end = o_end + week
        return occurrences

    def get_occupy_occurrence(self, start, end):
        o_start = self.start
        o_end = self.end

        occurrence = Occurrence(self.id, o_start, o_end, self.start, self.end, self.end_recurring_period, None,
                                None, None, None, False, 1)
        return occurrence

    def get_occurrence(self, o_start):

        occurrences = self.get_occurrence_list(o_start, o_start + timedelta(weeks=1))

        for o in occurrences:
            if o.start == o_start:
                return o

        return None

    def has_active_subscription(self, start, end):
        """
        1. the occurrence doesn't have appointment yet, it is active
        2. the occurrence has at least one appointment - confirmed, it is active
        3. the occurrence has one or more appointments - all are canceled, it is inactive

        """
        subscriptions = EventSubscription.objects.filter(event=self, start_time__lte=end, end_time__gt=start)

        for sub in subscriptions:
            occurrences = sub.get_occurrence_list(start, end)
            for o in occurrences:
                has_cancelled_appointment = False
                # logger.debug('start is {}, end is {}, occurrence is {}, subscription id is {}'.format(start, end, o.start, o.subscription_id))
                appointments = Appointment.objects.get_appointments_by_occurrence(o)
                for app in appointments:
                    # it has confirmed appointment
                    if app.status == Appointment.CONFIRMED:
                        return True
                    # it has cancelled appointment
                    else:
                        has_cancelled_appointment = True

                # at least there is one occurrence, which is to be confirmed - generating appointment
                if not has_cancelled_appointment:
                    return True

        return False



class EventSubscription(models.Model):

    event = ForeignKey(Event, on_delete=models.CASCADE)
    invitee = ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sub_invitees = models.ManyToManyField(User, related_name='sub_invitees')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    learning_group = models.ForeignKey(LearningGroup, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    objects = SubscriptionManager()

    class Meta:
        db_table = 'scheduler_eventsubscription'

    def __str__(self):
        return "%s %s %s %s %s (%s)" % (
            self.id,
            self.start_time,
            self.end_time,
            self.event,
            self.learning_group,
            ",members ".join(sub_invitee.username for sub_invitee in self.sub_invitees.all())
        )

    def get_occurrence_list(self, start, end):
        if start < self.start_time:
            start = self.start_time
        if end > self.end_time:
            end = self.end_time

        occurences = self.event.get_occurrence_list(start, end)
        for o in occurences:
            if o.start >= self.start_time and o.start < self.end_time:
                o.subscription_id = self.id
                o.subscription_start = self.start_time
                o.subscription_end = self.end_time
                o.subscription_invitee = self.sub_invitees
                if hasattr(self.learning_group, 'virtual_class_type'):
                    o.subscription_type = self.learning_group.virtual_class_type.type_name
        return occurences

    def get_occurrence_list_v2(self, start, end, student=None):
        '''
        start  end是查询的时间段的开始和结束
        :param subscription:
        :param start:
        :param end:
        :return:
        '''

        start_time = self.start_time
        end_time = self.end_time
        if end > end_time:
            end = end_time
        weeks = timedelta(weeks=1)
        subscription_occurrence_list = []
        members = Membership.objects.filter(learning_group_id=self.learning_group_id).all()
        if len(members) <= 0:
            return []
        while start_time < end:
            if start_time >= start:
                end_time = start_time + timedelta(minutes=55)
                appointments = Appointment.objects.filter(scheduled_time=start_time, event_subscription=self).all()
                # appoint_status = False  # 多次预约是否产生了appointment, 没有产生就说明没有取消
                has_virtualclass = False
                if len(appointments) > 0:
                    # for appointment in appointments:
                    #     if appointment.status == appointment.CONFIRMED:
                    has_virtualclass = True
                # else:
                #     appoint_status = True
                # if not appoint_status:
                #     start_time = start_time + weeks
                #     continue

                event = self.event
                student_names = []
                subscription_stu_name = None
                s_invitee = None
                for member in members:
                    if member.role == '1':
                        s_invitee = member.group_member.username
                        subscription_stu_name = member.group_member.username
                    student_names.append(member.group_member.username)
                if not s_invitee:
                    continue
                occurrence = Occurrence(event.id, start_time, end_time, event.start, event.end, event.end_recurring_period,
                                        self.id, self.start_time, self.end_time, s_invitee,
                                        is_available=True, is_occupied=2)
                occurrence.subscription_stu_name = subscription_stu_name
                occurrence.student_names = student_names
                occurrence.class_type_id = self.learning_group.virtual_class_type.id
                occurrence.learning_group = self.learning_group
                if start_time >= event.end_recurring_period:
                    occurrence.is_occupied = 1
                occurrence.has_virtualclass = has_virtualclass
                subscription_occurrence_list.append(occurrence)
            start_time = start_time + weeks
        return subscription_occurrence_list

    def get_virtual_event_occurrence_list(self, start):
        end = self.end_time
        # 如果 es 的结束时间小于等于event的period 就直接返回 event.get_occurrence_list
        if end <= self.event.end_recurring_period:
            return self.get_occurrence_list(start, end)
        # 若果 结束时间大于 event 的period, 先取出event. occurrences 之后要新建occurrence,添加到已有的occurrences中去
        occurrences = self.get_occurrence_list(start, self.event.end_recurring_period)

        occurrence_start = self.event.end_recurring_period - timedelta(minutes=45) + timedelta(days=7)
        occurrence_end = occurrence_start + timedelta(minutes=45)
        while end > occurrence_end:
            occurrence = Occurrence(self.event.id, occurrence_start, occurrence_end, self.event.start, self.event.end,
                                    self.event.end_recurring_period, self.id, self.start_time,
                                    self.end_time, self.invitee)
            occurrences.append(occurrence)
            occurrence_start = occurrence_start + timedelta(days=7)
            occurrence_end = occurrence_start + timedelta(minutes=45)
        return occurrences

    def get_occurrence(self, o_start):
        occurrences = self.get_occurrence_list(o_start, o_start + timedelta(weeks=1))

        for o in occurrences:
            if o.start == o_start:
                return o

        return None

    def has_reservation(self, start, end):
        '''
        if event subscription end_time is greater than event event_recurring_period, the rest occurrences are reservations.
        if reservation exists, new event_subscription can not be created.
        '''
        if self.end_time <= self.event.end_recurring_period:  # no reservation
            return False

        if not self.end_time > self.start_time:  # empty subscription
            return False

        t_current = self.event.start
        while t_current < self.end_time and t_current < end:
            if t_current >= self.event.end_recurring_period and t_current >= start:
                # apps = Appointment.objects.get_appointments(self, t_current)
                apps = Appointment.objects.filter(event_subscription=self, scheduled_time__gte=t_current)
                if len(apps) == 0:  # reservation doesn't have any appointment, it exists
                    return True
                else:
                    for app in apps:
                        # reservation has appointment, which isn't cancelled, it exists
                        if app.status != Appointment.CANCELLED:
                            return True
                t_current = t_current + timedelta(weeks=1)
            else:
                t_current = t_current + timedelta(weeks=1)
                continue

        return False

    def update_end_time(self, end):
        self.end_time = end
        self.save()

    def update_event(self, event):
        self.event = event
        self.save()


class Occurrence():

    def __init__(self, event_id, start, end, event_start, event_end, event_end_recurring_period, s_id, s_start, s_end,
                 s_invitee, class_type_id=None, is_available=True, is_occupied=0):
        self.event_id = event_id
        self.event_start = event_start
        self.event_end = event_end
        self.event_end_recurring_period = event_end_recurring_period
        self.start = start
        self.end = end
        self.class_type_id = class_type_id
        self.subscription_id = s_id
        self.subscription_start = s_start
        self.subscription_end = s_end
        self.subscription_invitee = s_invitee  # 班长
        self.is_available = is_available
        self.is_occupied = is_occupied

    def __eq__(self, other):
        return self.event_id == other.event_id

    def __hash__(self):
        return hash(('event_id', self.event_id))

    def __str__(self):
        return 'event id: {} {} {} is_available{} is_occupied{}'.format(
            self.event_id, self.start, self.end, self.is_available, self.is_occupied)


class Appointment(models.Model):


    CONFIRMED = 0
    CANCELLED = 1

    STATUS_CHOICES = (
        (CONFIRMED, 'CONFIRMED'),
        (CANCELLED, 'CANCELLED'),
    )
    original_start = models.DateTimeField()
    original_end = models.DateTimeField()
    scheduled_time = models.DateTimeField()
    hosts = models.ManyToManyField(User, related_name='hosts')
    invitees = models.ManyToManyField(User, related_name='invitees')
    learning_group = models.ForeignKey(LearningGroup, on_delete=models.CASCADE,
                                       null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=CONFIRMED)
    event_subscription = models.ForeignKey(EventSubscription, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    objects = AppointmentManager()

    def get_students(self):
        return AppointmentManager.get_student_by_order(self.learning_group, self.invitees)

    def get_monitors(self):
        return AppointmentManager.get_monitors(self.learning_group,self.invitees)

    students = property(get_students)
    monitors = property(get_monitors)


    def cancel(self, mute=False):
        self.status = Appointment.CANCELLED
        self.save()
    class Meta:
        db_table = 'scheduler_appointment'

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.scheduled_time, ','.join([h.username for h in self.hosts.all()]),
                                       ','.join([i.username for i in self.invitees.all()]))


class ChangeRequest(models.Model):
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    CONFIRMED = 'confirmed'

    INITIATOR_STUDENT = 'student'
    INITIATOR_TUTOR = 'tutor'

    requester = ForeignKey(User, related_name='requester', on_delete=models.CASCADE)
    approver = ForeignKey(User, related_name='approver', on_delete=models.CASCADE)
    appointment = ForeignKey(Appointment, on_delete=models.CASCADE)
    STATUS_CHOICE = (
        (PENDING, 'pending'),
        (CANCELLED, 'cancelled'),
        (CONFIRMED, 'confirmed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE)
    STATUS_TYPE_CHOICE = (
        (INITIATOR_STUDENT, 'student'),
        (INITIATOR_TUTOR, 'tutor')
    )
    change_type = models.CharField(max_length=10, choices=STATUS_TYPE_CHOICE)
    current_start = models.DateTimeField()
    event = ForeignKey(Event, on_delete=models.CASCADE)
    requested_start = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduler_changerequest'


class CanlenderDemo(models.Model):

    # MONDAY = 'Mon'
    # TUESDAY = 'Tue'
    # WEDNESDAY = 'Wed'
    # THURSDAY = 'Thu'
    # FRIDAY = 'Fri'
    # SATURDAY = 'Sat'
    # SUNDAY = 'Sun'
    #
    # WEEK_CHOICE = (
    #     (MONDAY, '星期一'),
    #     (TUESDAY, '星期二'),
    #     (WEDNESDAY, '星期三'),
    #     (THURSDAY, '星期四'),
    #     (FRIDAY, '星期五'),
    #     (SATURDAY, '星期六'),
    #     (SUNDAY, '星期天'),
    # )
    #
    # ACTIVE = 1
    # INACTIVE = 0
    #
    # ACTIVE_CHOICE = (
    #     (ACTIVE, 'active'),
    #     (INACTIVE, 'inactive'),
    # )
    #
    # week = models.CharField(max_length=10, choices=WEEK_CHOICE)
    # time = models.CharField(max_length=20)
    # is_active = models.BooleanField(choices=ACTIVE_CHOICE, default=ACTIVE)
    user = ForeignKey(User, on_delete=models.CASCADE)
    # calendar = models.CharField(max_length=5000, null=True, blank=True)
    calendar = models.TextField()


class TutorGrade(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.user.username, self.programme.programme_name, self.grade.get_grade_display())

    class Meta:
        db_table = 'tutor_tutorgrade'


class AppVersion(models.Model):
    appname = models.CharField(max_length=30)
    deviceid = models.CharField(max_length=100)
    devicename = models.CharField(max_length=30)
    versionnum = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appversion'
        unique_together = ("appname", "deviceid")

    def __str__(self):
        return self.deviceid + '-' + self.devicename + '-' + self.appname




# User Model extension.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.CharField(max_length=2000)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'userprofile_userprofile'

    User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class UserDetail(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(_("FirstName"), max_length=30, null=True, blank=True)
    last_name = models.CharField(_("LastName"), max_length=30, null=True, blank=True)

    GENDER_CHOICES = (
        ('Male', 1),
        ('Female', 2),
        ('N/A', 0),
    )
    gender = models.CharField(_("gender"), max_length=30, choices=GENDER_CHOICES, null=True,
                              blank=True)  # Male：男； Female：女
    birthdate = models.DateField(_("birthdate"), blank=True, null=True)
    phone_num = models.CharField(_("PhoneNumber"), max_length=30, null=True, blank=True)

    nationality = models.CharField(_("nationality"), max_length=2, choices=settings.COUNTRY_CHOICES, null=True,
                                   blank=True)
    country_of_residence = models.CharField(_("country_of_residence"), max_length=2, choices=settings.COUNTRY_CHOICES,
                                            null=True, blank=True)

    currency = models.CharField(_("currency"), max_length=3, choices=settings.CURRENCY_CHOICES)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'userprofile_userdetail'


class UserReferrer(models.Model):
    user = models.OneToOneField(User)
    referrer = ForeignKey(User, related_name='referrer', on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'userprofile_userreferrer'

    def __str__(self):
        return '{} by {}'.format(self.user.username, self.referrer.username)


def create_usercourse(user):
    programmes = Programme.objects.all()
    # if programmes.count() == 1:
    p = programmes.first()
    c = Course.objects.filter(programme=p).order_by('course_level').first()
    if c:
        uc = UserCourse(user=user, course=c, is_default=True, session_no=1)
        uc.save()
        return uc


# TODO : push message
class UserMessage(models.Model):
    user = models.ForeignKey(User, verbose_name=u"接收用户")
    course_no = models.IntegerField(blank=True, null=True)
    session_no = models.IntegerField(blank=True, null=True)
    message = models.CharField(max_length=500, verbose_name=u"消息内容")
    releated_url = models.CharField(max_length=500, verbose_name=u"相关路径", null=True)
    has_read = models.BooleanField(default=False, verbose_name=u"是否已读")
    add_time = models.DateTimeField(default=timezone.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"用户消息"
        verbose_name_plural = verbose_name
        db_table = 'userprofile_usermessage'


class ReferenceDataManager(models.Manager):

    def get_data_by_s1_source(self, s1, utm_source):
        try:
            data_list = ReferenceData.objects.filter(custom_s1=s1, utm_source=utm_source)
        except Exception as e:
            pass
        else:
            return data_list


# 记录用户通过分享注册的数据
class ReferenceData(models.Model):
    user = models.OneToOneField(User)
    custom_s1 = models.CharField(max_length=500)
    custom_s2 = models.CharField(max_length=500)
    custom_s3 = models.CharField(max_length=500)
    utm_source = models.CharField(max_length=500)
    utm_medium = models.CharField(max_length=500)
    utm_campaign = models.CharField(max_length=500)
    utm_term = models.CharField(max_length=500)
    utm_content = models.CharField(max_length=500)
    refurl = models.CharField(max_length=500, null=True)

    objects = ReferenceDataManager()

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'userprofile_referencedata'



import hashlib

import datetime
from django.db import models

from django.db.models.fields.related import ForeignKey

from django.contrib.auth.models import User
from .DynamicKey5 import *


logger = logging.getLogger(__name__)

# registered by pplingo@outlook.com
api_key = '45569802'
api_secret = 'bd18d53d03b50222656a397686c364445900d5f9'

# agora appid and appCertificate
appID = settings.AGORA_APP_ID
appCertificate = settings.AGORA_APP_CERTIFICATE

PROVIDER_OPENTOK = 'OPENTOK'
PROVIDER_AGORA = 'AGORA.IO'

MINUTES_IN_ADVANCE = 15  # 提前进课堂时间


class VirtualClassManager(models.Manager):

    def get_current_virtualclasses(self, queryset):
        datetime_now = datetime.datetime.now()
        datetime_end = datetime_now + datetime.timedelta(minutes=MINUTES_IN_ADVANCE)
        datetime_start = datetime_now - datetime.timedelta(minutes=115)
        vcs = queryset.filter(appointment__scheduled_time__gte=datetime_start).filter(
            appointment__scheduled_time__lt=datetime_end).filter(is_delivered=False)
        return vcs

    def get_past_virtualclasses(self, queryset):
        datetime_now = datetime.datetime.now()
        datetime_before_12months = datetime_now - datetime.timedelta(days=365)
        vcs = queryset.filter(appointment__scheduled_time__range=(datetime_before_12months, datetime_now)).filter(
            is_delivered=True).order_by('-appointment__scheduled_time')
        return vcs

    def get_future_virtualclasses(self, queryset):
        datetime_now = datetime.datetime.now()
        datetime_after_3months = datetime_now + datetime.timedelta(days=90)
        vcs = queryset.filter(appointment__scheduled_time__range=(datetime_now, datetime_after_3months)).filter(
            is_delivered=False).filter(appointment__status=Appointment.CONFIRMED).order_by(
            'appointment__scheduled_time')
        return vcs

    @staticmethod
    def one_virtualclass_is_delivered(user):
        is_one_delivered = VirtualClass.objects.filter(appointment__invitees__in=[user], is_delivered=True).exists()
        return is_one_delivered

    def is_have_undelivered_virtualclass(self, user):
        virtual_classes = self.filter(is_delivered=False,
                                      appointment__invitees=user).exists()
        return virtual_classes

    @staticmethod
    def get_all_monitor_by_user(appointment):
        return Membership.objects.get_monitor_of_group(appointment.invitees.first())


# Create your models here.
class VirtualClass(models.Model):
    NORMAL = 0
    STUDENT_ABSENCE = 1  # 学生缺席
    STUDENT_EQUIPMENT_ABNORMAL = 2  # 学生设备或网络故障
    TUTOR_ABSENCE = 11  # 教师缺席
    TUTOR_EQUIPMENT_ABNORMAL = 12  # 老师设备或网络故障
    OTHER_REASON = 20  # 其他
    CLASS_NOONE = 21  # 学生老师均未出席

    REASON_CHOICES = (
        (NORMAL, _('NORMAL')),
        (STUDENT_ABSENCE, _('STUDENT_ABSENCE')),
        (STUDENT_EQUIPMENT_ABNORMAL, _('STUDENT_EQUIPMENT_ABNORMAL')),
        (TUTOR_ABSENCE, _('TUTOR_ABSENCE')),
        (TUTOR_EQUIPMENT_ABNORMAL, _('TUTOR_EQUIPMENT_ABNORMAL')),
        (OTHER_REASON, _('OTHER_REASON')),
        (CLASS_NOONE, _('CLASS_NOONE')),
    )

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(null=True, blank=True, max_length=100)
    course_session = ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)  # session ID 对应cw
    is_delivered = models.BooleanField(default=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    end_reason = models.IntegerField(choices=REASON_CHOICES, null=True, blank=True)
    end_reason_description = models.CharField(max_length=500, null=True, blank=True)

    Agaro = 'Agaro'
    Tk = 'Tk'
    TYPE_CHOICES = (
        (Agaro, 'Agaro'),
        (Tk, 'Tk'),
    )

    virtualclass_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default=Agaro)
    tk_class_id = models.CharField(null=True, blank=True, max_length=100)

    objects = VirtualClassManager()

    def _get_original_start(self):
        return self.appointment.original_start

    def _get_original_end(self):
        return self.appointment.original_end

    origial_start = property(_get_original_start)
    origial_end = property(_get_original_end)

    def get_scheduled_time(self):
        return self.appointment.scheduled_time

    def get_tutors(self):
        return self.appointment.hosts

    def get_appointment_student(self):
        return self.appointment.students

    def get_students(self):
        return VirtualClassManager.get_student_by_order(self.appointment)

    def get_students_monitor(self):
        return VirtualClassManager.get_all_monitor_by_user(self.appointment)

    def get_class_type(self):
        if hasattr(self.class_type, 'type_name'):
            return self.class_type.type_name

    scheduled_time = property(get_scheduled_time)
    tutors = property(get_tutors)
    students = property(get_appointment_student)  # 根据student的 类型创建vc
    students_monitor = property(get_students_monitor)
    ROLE_TUTOR = 'tutor'
    ROLE_STUDENT = 'student'

    def _get_api_key(self):
        return api_key

    api_key = property(_get_api_key)

    class Meta:
        db_table = 'virtualclass_virtualclass'

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.appointment.scheduled_time,
                                       ','.join([h.username for h in self.appointment.hosts.all()]),
                                       ','.join([i.username for i in self.appointment.invitees.all()]))


class UserClassType(models.Model):
    user = models.OneToOneField(User, unique=True)
    Agaro = 'Agaro'
    Tk = 'Tk'
    TYPE_CHOICES = (
        (Agaro, 'Agaro'),
        (Tk, 'Tk'),
    )

    virtualclass_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default=Tk)

    class Meta:
        db_table = 'virtualclass_userclasstype'

    def __str__(self):
        return self.user.username


class ClassEvaluation(models.Model):
    user = ForeignKey(User, related_name='evaluatee', on_delete=models.CASCADE)
    virtual_class = ForeignKey(VirtualClass, on_delete=models.CASCADE)
    ROLES = (
        ('Tutor', 'Tutor'),
        ('Student', 'Student'),
    )
    user_role = models.CharField(max_length=7, choices=ROLES)
    EVALUATION_CATEGORY = (
        ('PQ', 'Practice Consistency and Quality'),  # student
        ('SP', 'Skills and Progress'),  # student
        ('AR', 'Attitude and Responsibility'),  # student
        ('PK', 'Professional Knowledge'),  # tutor
        ('ID', 'Instructional Delivery'),  # tutor
        ('LE', 'Learning Environment'),  # tutor
        ('OT', 'On-time record'),  # tutor
    )
    category = models.CharField(max_length=3, choices=EVALUATION_CATEGORY)
    score = models.IntegerField(default=4)
    create_time = models.DateTimeField(auto_now_add=True)
    evaluator = ForeignKey(User, related_name='evaluator', on_delete=models.CASCADE)

    class Meta:
        db_table = 'virtualclass_classevaluation'


class ClassComment(models.Model):
    user = ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    virtual_class = ForeignKey(VirtualClass, on_delete=models.CASCADE)
    ROLES = (
        ('Tutor', 'Tutor'),
        ('Student', 'Student'),
    )
    user_role = models.CharField(max_length=7, choices=ROLES)
    comment = models.CharField(max_length=512)
    create_time = models.DateTimeField(auto_now_add=True)
    commentor = ForeignKey(User, related_name='commentor', on_delete=models.CASCADE)

    class Meta:
        db_table = 'virtualclass_classcomment'

def get_channel_key(channelName):
    unixts = int(time.time());
    uid = 0
    randomint = -2147483647
    expiredts = 0

    # dynamic_key_value = generateMediaChannelKey(appID, appCertificate, channelName, unixts, randomint, uid, expiredts)
    dynamic_key_value = settings.AGORA_VIDEO_APP_ID

    return dynamic_key_value


def get_signalling_key(account):
    ts = str(int(time.time()) + 3600)
    signalling_key = '1:' + appID
    signalling_key = signalling_key + ':' + ts
    logger.debug('key = {}'.format(signalling_key))

    raw = account + appID + appCertificate + ts
    # logger.debug('raw = {}'.format(raw))

    m = hashlib.md5()
    m.update(raw.encode('utf-8'))
    digest = m.hexdigest()

    signalling_key = '{}:{}'.format(signalling_key, digest)

    # demo key
    # signalling_key = "E33D67E2B174495F8F7AB9E154713D5E"

    # appID
    # signalling_key = "341C6C0733234DA384218CFBC4BB30DB"
    logger.debug('key = {}'.format(signalling_key))

    return signalling_key


def get_video_service_provider(virtual_class):
    if settings.VIDEO_SERVICE_PROVIDER:
        default_provider = settings.VIDEO_SERVICE_PROVIDER
    else:
        default_provider = PROVIDER_AGORA

    try:
        session_id = virtual_class.session_id
    except AttributeError:
        try:
            vc = VirtualClass.objects.get(id=virtual_class)
            session_id = vc.session_id
        except VirtualClass.DoesNotExist:
            return None

    if not session_id:
        return PROVIDER_AGORA
    else:
        return default_provider


def get_signalling_service_provider(virtual_class):
    if settings.SIGNALLING_SERVICE_PROVIDER:
        default_provider = settings.SIGNALLING_SERVICE_PROVIDER
    else:
        default_provider = PROVIDER_OPENTOK

    try:
        session_id = virtual_class.session_id
    except AttributeError:
        try:
            vc = VirtualClass.objects.get(id=virtual_class)
            session_id = vc.session_id
        except VirtualClass.DoesNotExist:
            return None

    if not session_id:
        return PROVIDER_AGORA
    else:
        return default_provider


class VirtualclassResource(models.Model):
    virtualclass = models.OneToOneField("VirtualClass", on_delete=models.CASCADE)
    ext_course_id = models.IntegerField()

    class Meta:
        db_table = 'virtualclass_virtualclassresource'

    # objects = VirtualclassResourceManager()


class StudentInOutTime(models.Model):
    virtualclass = models.ForeignKey(VirtualClass, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    in_class_time = models.DateTimeField()
    out_class_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'virtualclass_studentinouttime'


class TkClassVideo(models.Model):
    virtualclass = models.ForeignKey(VirtualClass, on_delete=models.CASCADE)
    video_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='s3视频地址')
    tk_video_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='拓客视频地址')

    class Meta:
        db_table = 'virtualclass_tkclassvideo'


class CmsUser(models.Model):
    ACTIVE = 1
    FORBID = 0
    IS_ACTIVE = (
        (ACTIVE, 'active'),
        (FORBID, 'forbid')
    )

    username = models.CharField(max_length=50, unique=True)
    realname = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    salt = models.CharField(max_length=6, verbose_name='加盐值', help_text='password经过加盐进行md5加密')
    email = models.EmailField(blank=True, null=True)
    work_address = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    is_active = models.BooleanField(choices=IS_ACTIVE, default=ACTIVE, verbose_name='该用户是否启用 1:启用，2:禁止')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}--{}'.format(self.username, self.get_is_active_display())

    def save(self, *args, **kwargs):
        # salt = kwargs.get('salt')
        # password = kwargs.get('password')
        # if salt and password:
        # self.password = encrypt_passwd(self.password, self.salt)
        super(CmsUser, self).save(*args, **kwargs)

    class Meta:
        db_table = 'manager_user'


class ExtStudent(models.Model):

    PAY_ACTION = (
        (1, '低'),
        (2, '中'),
        (3, '高')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # phone_num = models.CharField(max_length=30, null=True, blank=True)
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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manager_ext_student'


class LearnManagerStudent(models.Model):
    '''
    学管老师负责的学生
    '''

    ACTIVE = 1  # 有效
    CANCEL = 0  # 无效

    STUDENT_STATUS = (
        (ACTIVE, 'active'),
        (CANCEL, 'cancel')
    )

    cms_user = models.ForeignKey(CmsUser, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STUDENT_STATUS, default=ACTIVE, verbose_name='接受情况')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='学管老师接管学生时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='更换学管老师时间')

    class Meta:
        db_table = 'manager_learnmanager_student'


class CourseAdviserStudent(models.Model):
    '''
    课程顾问负责的学生
    '''

    ACTIVE = 1  # 有效
    CANCEL = 0  # 无效

    STUDENT_STATUS = (
        (ACTIVE, 'active'),
        (CANCEL, 'cancel')
    )

    cms_user = models.ForeignKey(CmsUser, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STUDENT_STATUS, default=ACTIVE, verbose_name='状态')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='课程顾问接管学生时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='更换课程顾问时间')

    class Meta:
        db_table = 'manager_courseadviser_student'


class GeneralCode(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(_("code"), max_length=10, default='', blank=True)
    is_used = models.IntegerField(default=0)

    def __str__(self):
        return 'user:{} code:{} is_used{}'.format(self.user, self.code, self.is_used)
    class Meta:
        db_table = 'ambassador_generalcode'


class PaypalIpn(models.Model):

    '''paypal支付表'''

    business = models.CharField(max_length=127)
    charset = models.CharField(max_length=31)
    custom = models.CharField(max_length=127)
    notify_version = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    parent_txn_id = models.CharField(max_length=31)
    receiver_email = models.CharField(max_length=127)
    receiver_id = models.CharField(max_length=127)
    residence_country = models.CharField(max_length=15)
    test_ipn = models.IntegerField()
    txn_id = models.CharField(max_length=127)
    txn_type = models.CharField(max_length=127)
    verify_sign = models.CharField(max_length=127)
    address_country = models.CharField(max_length=63)
    address_city = models.CharField(max_length=63)
    address_country_code = models.CharField(max_length=63)
    address_name = models.CharField(max_length=127)
    address_state = models.CharField(max_length=63)
    address_status = models.CharField(max_length=127)
    address_street = models.CharField(max_length=127)
    address_zip = models.CharField(max_length=31)
    contact_phone = models.CharField(max_length=31)
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)
    payer_business_name = models.CharField(max_length=127)
    payer_email = models.CharField(max_length=127)
    payer_id = models.CharField(max_length=15)
    auth_amount = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    auth_exp = models.CharField(max_length=31)
    auth_id = models.CharField(max_length=31)
    auth_status = models.CharField(max_length=127)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    invoice = models.CharField(max_length=127)
    item_name = models.CharField(max_length=127)
    item_number = models.CharField(max_length=127)
    mc_currency = models.CharField(max_length=31)
    mc_fee = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_gross = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_handling = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_shipping = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    memo = models.CharField(max_length=127)
    num_cart_items = models.IntegerField(blank=True, null=True)
    option_name1 = models.CharField(max_length=63)
    option_name2 = models.CharField(max_length=63)
    payer_status = models.CharField(max_length=127)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_gross = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    payment_status = models.CharField(max_length=127)
    payment_type = models.CharField(max_length=127)
    pending_reason = models.CharField(max_length=127)
    protection_eligibility = models.CharField(max_length=127)
    quantity = models.IntegerField(blank=True, null=True)
    reason_code = models.CharField(max_length=127)
    remaining_settle = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    settle_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    settle_currency = models.CharField(max_length=31)
    shipping = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    shipping_method = models.CharField(max_length=127)
    tax = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    transaction_entity = models.CharField(max_length=127)
    auction_buyer_id = models.CharField(max_length=63)
    auction_closing_date = models.DateTimeField(blank=True, null=True)
    auction_multi_item = models.IntegerField(blank=True, null=True)
    for_auction = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    amount_per_cycle = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    initial_payment_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    next_payment_date = models.DateTimeField(blank=True, null=True)
    outstanding_balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    payment_cycle = models.CharField(max_length=127)
    period_type = models.CharField(max_length=127)
    product_name = models.CharField(max_length=127)
    product_type = models.CharField(max_length=127)
    profile_status = models.CharField(max_length=127)
    recurring_payment_id = models.CharField(max_length=127)
    rp_invoice_id = models.CharField(max_length=127)
    time_created = models.DateTimeField(blank=True, null=True)
    amount1 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    amount2 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    amount3 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_amount1 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_amount2 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    mc_amount3 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    password = models.CharField(max_length=31)
    period1 = models.CharField(max_length=127)
    period2 = models.CharField(max_length=127)
    period3 = models.CharField(max_length=127)
    reattempt = models.CharField(max_length=15)
    recur_times = models.IntegerField(blank=True, null=True)
    recurring = models.CharField(max_length=15)
    retry_at = models.DateTimeField(blank=True, null=True)
    subscr_date = models.DateTimeField(blank=True, null=True)
    subscr_effective = models.DateTimeField(blank=True, null=True)
    subscr_id = models.CharField(max_length=31)
    username = models.CharField(max_length=63)
    case_creation_date = models.DateTimeField(blank=True, null=True)
    case_id = models.CharField(max_length=127)
    case_type = models.CharField(max_length=127)
    receipt_id = models.CharField(max_length=127)
    currency_code = models.CharField(max_length=31)
    handling_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    transaction_subject = models.CharField(max_length=127)
    ipaddress = models.CharField(max_length=31, blank=True, null=True)
    flag = models.IntegerField()
    flag_code = models.CharField(max_length=15)
    flag_info = models.CharField(max_length=2047)
    query = models.CharField(max_length=2047)
    response = models.CharField(max_length=2047)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    from_view = models.CharField(max_length=15, blank=True, null=True)
    mp_id = models.CharField(max_length=127, blank=True, null=True)
    option_selection1 = models.CharField(max_length=127)
    option_selection2 = models.CharField(max_length=127)

    class Meta:
        managed = False
        db_table = 'paypal_ipn'


class TutorSalary(models.Model):

    PAYMENTED = 1
    UNPAY = 0
    PAY_STATUS = (
        (PAYMENTED, 1),
        (UNPAY, 0)
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_salary')
    lesson_num = models.IntegerField(default=0, verbose_name='本月上课课时')
    delivery_salary = models.FloatField(default=0.0, verbose_name='基本工资')
    incentive_salary = models.FloatField(default=0.0, verbose_name='奖励工资')
    absenc_compensation_salary = models.FloatField(default=0.0, verbose_name='学生缺席老师奖励工资')
    no_show_salary = models.FloatField(default=0.0, verbose_name='老师缺席罚金')
    data_date = models.CharField(max_length=10, default='', verbose_name='教师工资月份')
    student_num = models.FloatField(default=0.0, verbose_name='本月学生数量')
    pay_status = models.BooleanField(choices=PAY_STATUS, default=0)
    pay_user = models.ForeignKey(User, null=True, blank=True, related_name='pay_tutor_salary')
    order_no = models.CharField(max_length=50, null=True, blank=True, verbose_name='转账流水号')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tutor_tutorsalary'
        unique_together = ('user', 'data_date',)
