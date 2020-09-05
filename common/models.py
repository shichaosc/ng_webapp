from django.db import models
from classroom.models import ClassType
from tutor.models import TutorInfo, UserLevel
from course.models import CourseEdition
from django.conf import settings
from ambassador.models import UserAmbassadorInfo


class CommonAmbassadorCode(models.Model):

    '''城市合伙人推广码'''

    NO_USE = 0
    USED = 1

    IS_USERD_CHOICE = (
        (NO_USE, 'No Use'),
        (USED, 'Used')
    )

    ambassador_user = models.ForeignKey(UserAmbassadorInfo, models.CASCADE, blank=True, null=True)
    code = models.CharField(max_length=15)
    is_used = models.IntegerField(choices=IS_USERD_CHOICE, default=NO_USE, help_text='是否已使用')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'common_ambassador_code'

    def __str__(self):
        return '{}-{}'.format(self.ambassador_user, self.code)


class CommonAppversion(models.Model):

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

    role = models.IntegerField(choices=ROLE_CHOICE, blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    appname = models.CharField(max_length=63, verbose_name='APP名字，PPChinese Connect')
    deviceid = models.CharField(unique=True, max_length=127, verbose_name='设备标识')
    devicename = models.CharField(max_length=31, verbose_name='设备名称')
    versionnum = models.CharField(max_length=15, verbose_name='APP版本号')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'common_appversion'


class CommonBussinessRule(models.Model):

    '''
    规则类型
    1：BASE_PAY；
    2：INCENTIVE_PAY；
    3：TOPUP_BONUS；
    4：REFERRAL_INCENTIVE；
    5：REFERRAL_BONUS
    '''
    BASE_PAY = 1
    INCENTIVE_PAY = 2
    TOPUP_BONUS = 3
    REFERRAL_INCENTIVE = 4  # 被推荐人
    REFERRAL_BONUS = 5  # 推荐人
    GROUP_BONUS = 6  # 团购
    SG_REFERRAL_BONUS = 7  # sg推荐人奖励
    PARTNER_REFERRAL_BONUS = 8  # 城市合伙人的推荐奖励

    ROLE_TYPE_CHOICE = (
        (BASE_PAY, 'Base Pay'),
        (INCENTIVE_PAY, 'Incentive Pay'),
        (TOPUP_BONUS, 'Topup Bonus'),
        (REFERRAL_INCENTIVE, 'Referral Incentive'),
        (REFERRAL_BONUS, 'Referral Bonus'),
        (GROUP_BONUS, 'Group Bonus'),
        (SG_REFERRAL_BONUS, 'SG Referral Bonus'),
        (PARTNER_REFERRAL_BONUS, 'Partner Referral Bonus')
    )

    SINGAPORE = 1
    OTHER_AREA = 2

    LOCAL_AREA_CHOICE = (
        (SINGAPORE, 'Singapore'),
        (OTHER_AREA, 'Other Area')
    )

    course_edition = models.ForeignKey(CourseEdition, models.CASCADE, blank=True, null=True)
    class_type = models.ForeignKey(ClassType, models.CASCADE, blank=True, null=True)
    local_area = models.IntegerField(choices=LOCAL_AREA_CHOICE, blank=True, null=True)
    # rule_type = models.IntegerField(choices=ROLE_TYPE_CHOICE)
    rule_type = models.IntegerField(help_text='规则类型，1：BASE_PAY；2：INCENTIVE_PAY；3：TOPUP_BONUS；4：REFERRAL_INCENTIVE；5：REFERRAL_BONUS')
    user_level = models.ForeignKey(UserLevel, models.CASCADE, blank=True, null=True)
    valid_start = models.DateTimeField(help_text='有效期开始时间')
    valid_end = models.DateTimeField(help_text='有效期结束时间')
    remark = models.CharField(max_length=127)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'common_bussiness_rule'

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.course_edition, self.class_type, self.rule_type, self.user_level)


class CommonCoupon(models.Model):

    INVALID = 0
    VALID = 1

    STATUS_CHOICE = (
        (INVALID, 'invalid'),
        (VALID, 'valid')
    )

    NORMAL_ACCOUNT = 1  # 标准课时
    PRIVATE_ACCOUNT = 2  # 定向课时

    ACCOUNT_CHOICE = (
        (NORMAL_ACCOUNT, 'NORMAL_ACCOUNT'),
        (PRIVATE_ACCOUNT, 'PRIVATE_ACCOUNT')
    )

    code = models.CharField(unique=True, max_length=127)
    valid_start_time = models.DateTimeField(verbose_name='有效期开始时间')
    valid_end_time = models.DateTimeField(verbose_name='有效期结束时间')
    amount = models.IntegerField(default=0, verbose_name='使用该优惠码最少充值课时')
    max_amount = models.IntegerField(default=0, verbose_name='使用该优惠码最大充值课时')
    discount = models.DecimalField(max_digits=18, decimal_places=6, help_text='折扣比例，百分比')
    status = models.IntegerField(choices=STATUS_CHOICE)
    account_class = models.IntegerField(choices=ACCOUNT_CHOICE, null=True, blank=True, help_text='分类，1:标准课时；2:定向课时')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'common_coupon'


class ExchangeRate(models.Model):

    '''货币汇率，货币单价/课时'''

    DISPLAY = 1
    HIDDEN = 0

    REACHARGE_CHOICE = (
        (DISPLAY, 'Display'),
        (HIDDEN, 'Hidden')
    )

    currency = models.CharField(max_length=15, help_text='货币名称')
    currency_en = models.CharField(max_length=255, blank=True, null=True)
    currency_zh = models.CharField(max_length=255, blank=True, null=True)
    rate = models.DecimalField(max_digits=18, decimal_places=6, help_text='货币汇率，一个课时的货币单价')
    valid_start = models.DateTimeField(help_text='有效期开始时间')
    valid_end = models.DateTimeField(help_text='有效期开始时间')
    recharge = models.IntegerField(choices=REACHARGE_CHOICE, default=HIDDEN, help_text='充值货币列表中是否显示')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    default_currency = settings.CNY

    def __str__(self):
        return '{}-{}'.format(self.currency, self.rate)

    class Meta:
        managed = False
        db_table = 'common_exchange_rate'


class CommonRuleFormula(models.Model):
    rule = models.ForeignKey(CommonBussinessRule, models.CASCADE)
    min_amount = models.IntegerField(help_text='最少节课')
    max_amount = models.IntegerField(help_text='最多节课')
    amount = models.DecimalField(max_digits=18, decimal_places=6, help_text='课时')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'common_rule_formula'


class CommonStudentCoupon(models.Model):

    '''学生注册优惠码'''

    DISPLAY = 1
    HIDDEN = 0

    STATUS_CHOICE = (
        (DISPLAY, 'Display'),
        (HIDDEN, 'Hidden')
    )

    code = models.CharField(unique=True, max_length=127)
    valid_start = models.DateTimeField()
    valid_end = models.DateTimeField()
    discount = models.IntegerField(help_text='折扣比例，百分比')
    status = models.IntegerField(choices=STATUS_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.code, self.discount, self.discount)

    class Meta:
        managed = False
        db_table = 'common_student_coupon'


class UserConfig(models.Model):

    '''用户配置信息表'''

    user_id = models.BigIntegerField(verbose_name='用户标识')
    role = models.IntegerField(verbose_name='用户角色')
    config_key = models.CharField(max_length=63, verbose_name='配置key')
    config_content = models.CharField(max_length=4095, verbose_name='配置内容，json格式')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.user_id, self.role, self.config_key)

    class Meta:
        managed = False
        db_table = 'common_user_config'
        unique_together = ('user_id', 'role', 'config_key')
