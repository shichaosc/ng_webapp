from django.db import models
from classroom.models import ClassType, ClassInfo
from course.models import CourseEdition
from common.models import CommonCoupon
from student.models import UserStudentInfo, UserParentInfo
from tutor.models import TutorInfo
from django.utils import timezone
from django.db import transaction
import uuid
from finance.utils import get_currency_id, get_currency, get_currency_rate


# class ActivateCard(models.Model):
#     '''学生开卡记录'''
#     ACTIVE = 1
#     INVALID = 0
#
#     STATUS_CHOICE = (
#         (ACTIVE, 'Active'),
#         (INVALID, 'Invalid')
#     )
#     code = models.CharField(unique=True, max_length=63)
#     user = models.ForeignKey(UserBaseInfo, models.CASCADE)
#     reason = models.IntegerField()
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     discount = models.IntegerField()
#     status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE)
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         managed = False
#         db_table = 'finance_activate_card'


class AccountBalance(models.Model):

    TOPUP_AMOUNT = 1
    BONUS_AMOUNT = 2
    ACTIVITY_AMOUNT = 3

    TYPE_CHOICE = (
        (TOPUP_AMOUNT, 'TOPUP_AMOUNT'),
        (BONUS_AMOUNT, 'BONUS_AMOUNT'),
        (ACTIVITY_AMOUNT, 'ACTIVITY_AMOUNT')
    )

    NORMAL_ACCOUNT = 1
    PRIVATE_ACCOUNT = 2

    ACCOUNT_CHOICE = (
        (NORMAL_ACCOUNT, 'NORMAL_ACCOUNT'),
        (PRIVATE_ACCOUNT, 'PRIVATE_ACCOUNT')
    )

    NOT_DELETE = 0
    DELETED = 1

    STATE_CHOICE = (
        (NOT_DELETE, 'Not Delete'),
        (DELETED, 'Deleted')
    )

    parent_user = models.ForeignKey(UserParentInfo, on_delete=models.CASCADE, help_text='家长用户id')
    type = models.IntegerField(choices=TYPE_CHOICE, help_text='1:正常课时;2:赠送课时;3:运营课时')
    account_class = models.IntegerField(choices=ACCOUNT_CHOICE, help_text='账户分类 1:标准课时 ;2:定向课时')
    balance = models.DecimalField(max_digits=18, decimal_places=6, help_text='课时余额')
    rate = models.DecimalField(max_digits=18, decimal_places=6, help_text='折扣率')
    status = models.IntegerField(null=False, blank=False, help_text='账户状态 0:正常;1:过期')
    state = models.IntegerField(choices=STATE_CHOICE, default=NOT_DELETE, help_text='状态 0:正常;1:删除')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.parent_user.username, self.balance)

    class Meta:

        managed = False
        db_table = 'accounts_balance'


class BalanceChange(models.Model):
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
    REDEEM = 16  # redeem 课程卡
    REFERRAL_TRIAL = 17  # referrer receives, while referee takes trial class
    REFERRAL_INCENTIVE = 18  # referee receives, while himself/herself top-up
    FIRST_COURSE_REWARD = 19  # 被推荐人上完试听课后给被推荐人1课时奖励
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

    role = models.IntegerField(choices=ROLE_CHOICE)
    user_id = models.BigIntegerField()
    reason = models.IntegerField(choices=REASON_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    normal_amount = models.DecimalField(max_digits=18, decimal_places=6)
    reference = models.CharField(max_length=1023)
    parent_user_id = models.BigIntegerField(verbose_name='家长id', null=True, blank=True)
    adviser_user_id = models.IntegerField(null=True, blank=True, verbose_name='课程顾问id')
    xg_user_id = models.IntegerField(null=True, blank=True, verbose_name='学管id')
    balance = models.ForeignKey(AccountBalance, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.reference, self.get_reason_display(), self.amount)

    def save(self, *args, **kwargs):
        role = self.role
        if role == BalanceChange.TEACHER:
            if self.amount:
                tutor = TutorInfo.objects.get(id=self.user_id)
                tutor.balance = tutor.balance + self.amount
                tutor.save()
        else:
            balance_id = self.balance_id
            if balance_id:
                account_balance = AccountBalance.objects.filter(id=balance_id).first()
                account_balance.balance = account_balance.balance + self.amount
                account_balance.save()
        super(BalanceChange, self).save(*args, **kwargs)

    @staticmethod
    def save_balance_change(role, user_id, reference, reason, amount, parent_user_id=None, adviser_user_id=None, xg_user_id=None, normal_amount=0, balance_id=None):
        balance_change = BalanceChange()
        balance_change.reason = reason
        balance_change.amount = amount
        balance_change.reference = reference
        balance_change.user_id = user_id
        balance_change.parent_user_id = parent_user_id
        balance_change.adviser_user_id = adviser_user_id
        balance_change.xg_user_id = xg_user_id
        balance_change.role = role
        balance_change.normal_amount = normal_amount
        balance_change.balance_id = balance_id
        balance_change.save()
        #
        # if role == BalanceChange.TEACHER:
        #     tutor_info = TutorInfo.objects.filter(id=user_id).first()
        #     tutor_info.balance = tutor_info.balance +

    class Meta:
        managed = False
        db_table = 'finance_balance_change'


class BalanceChangeNew(models.Model):  # 导入数据用
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
    REDEEM = 16  # redeem 课程卡
    REFERRAL_TRIAL = 17  # referrer receives, while referee takes trial class
    REFERRAL_INCENTIVE = 18  # referee receives, while himself/herself top-up
    FIRST_COURSE_REWARD = 19  # 被推荐人上完试听课后给被推荐人1课时奖励
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

    role = models.IntegerField(choices=ROLE_CHOICE)
    user_id = models.BigIntegerField()
    reason = models.IntegerField(choices=REASON_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    reference = models.CharField(max_length=1023)
    normal_amount = models.DecimalField(max_digits=18, decimal_places=6)
    parent_user_id = models.BigIntegerField(verbose_name='家长id', null=True, blank=True)
    adviser_user_id = models.IntegerField(null=True, blank=True, verbose_name='课程顾问id')
    xg_user_id = models.IntegerField(null=True, blank=True, verbose_name='学管id')
    # balance = models.ForeignKey(AccountBalance, null=True, blank=True)
    create_time = models.DateTimeField(default=timezone.now())
    # create_time = models.DateTimeField(auto_now_add=True)
    # update_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(default=timezone.now())

    # def __str__(self):
    #     return '{}-{}-{}'.format(self.user.__str__(), self.get_reason_display(), self.amount)

    @staticmethod
    def save_balance_change(role, user_id, reference, reason, amount, parent_user_id=None, adviser_user_id=None, xg_user_id=None):
        balance_change = BalanceChange()
        balance_change.reason = reason
        balance_change.amount = amount
        balance_change.reference = reference
        balance_change.user_id = user_id
        balance_change.parent_user_id = parent_user_id
        balance_change.adviser_user_id = adviser_user_id
        balance_change.xg_user_id = xg_user_id
        balance_change.role = role
        balance_change.save()

    class Meta:
        managed = False
        db_table = 'finance_balance_change'


class CoursePackage(models.Model):

    '''课程包'''

    YEAR = 3
    MONTH = 2
    DAY = 1

    DURATION_TYPE_CHOICE = (
        (YEAR, 'Year'),
        (MONTH, 'Month'),
        (DAY, 'Day')
    )

    class_type = models.ForeignKey(ClassType, models.DO_NOTHING)
    # course_edition = models.ForeignKey(CourseEdition, models.DO_NOTHING)
    course_edition_id = models.CharField(max_length=127)
    valid_start_time = models.DateTimeField()
    valid_end_time = models.DateTimeField()
    valid_days = models.IntegerField()
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='美元价格')
    max_stock = models.IntegerField()
    user_limit = models.IntegerField()
    # duration = models.IntegerField(verbose_name='周期时长')
    # duration_type = models.IntegerField(choices=DURATION_TYPE_CHOICE, verbose_name='周期类型')
    # cash_price = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='美元价格')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_course_package'


class BuyPackage(models.Model):

    '''学生购买的课程包'''

    course_package = models.ForeignKey(CoursePackage, models.CASCADE)
    class_type = models.ForeignKey(ClassType, models.CASCADE)
    course_edition = models.ForeignKey(CourseEdition, models.CASCADE)
    parent_user = models.ForeignKey(UserParentInfo, models.CASCADE)
    valid_start_time = models.DateTimeField(verbose_name='有效期开始时间')
    valid_end_time = models.DateTimeField(verbose_name='有效期结束时间')
    amount = models.IntegerField(verbose_name='课程包包含课时数')
    remain_amount = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='剩余课时数')
    order_no = models.CharField(max_length=127, verbose_name='订单编号')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_buy_package'


class ClasstypePrice(models.Model):

    '''各班型和课程版本的课时单价'''

    NORMAL_AMOUNT = 1
    PRIVATE_AMOUNT = 2

    ACCOUNT_CLASS_CHOICE = (
        (NORMAL_AMOUNT, 'Normal Amount'),
        (PRIVATE_AMOUNT, 'Private Amount')
    )

    class_type = models.ForeignKey(ClassType, models.DO_NOTHING)
    course_edition = models.ForeignKey(CourseEdition, models.DO_NOTHING)
    prices = models.DecimalField(max_digits=18, decimal_places=6)
    account_class = models.IntegerField(choices=ACCOUNT_CLASS_CHOICE, default=NORMAL_AMOUNT, help_text='账户分类 1:标准课时 ;2:定向课时')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_classtype_price'


class RechargeOrder(models.Model):

    '''充值订单表'''

    NOMAL = 1
    RECHARGE_CARD = 2
    PACKAGE = 3

    RECHARGE_CHOICE = (
        (NOMAL, '普通'),
        (RECHARGE_CARD, '充值卡'),
        (PACKAGE, '课程包'),
    )

    UNPAID = 0
    PAID = 1
    FAIL_PAID = 2
    REFUND = 3
    CANCEL_ORDER = 4


    STATUS_CHOICE = (
        (UNPAID, 'Unpaid'),
        (PAID, 'Paid'),
        (FAIL_PAID, 'Fail Paid'),
        (REFUND, 'Refund'),
        (CANCEL_ORDER, 'Cancel Order')

    )

    # CURRENCY_ID_CHOICE = get_currency_id()

    FIRST_RECHARGE = 1
    NOT_FIRST_RECHARGE = 0

    FIRST_RECHARGE_CHOICE = (
        (FIRST_RECHARGE, 'First Recharge'),
        (NOT_FIRST_RECHARGE, 'Not First Recharge')
    )

    CARD = 'card'
    ALIPAY = 'alipay'
    WECHAT = 'wechat'

    PAY_STATUS_CHOICE = (
        (CARD, 'Card'),
        (ALIPAY, 'Alipay'),
        (WECHAT, 'Wechat')
    )

    order_no = models.CharField(unique=True, max_length=63, default=uuid.uuid4)
    parent_user = models.ForeignKey(UserParentInfo, models.CASCADE, related_name='reaharge_order')
    recharge_type = models.IntegerField(choices=RECHARGE_CHOICE, default=NOMAL)
    course_package = models.ForeignKey(CoursePackage, models.CASCADE, blank=True, null=True)
    sg_class = models.ForeignKey(ClassInfo, null=True, blank=True)
    code = models.CharField(max_length=63, blank=True, null=True, verbose_name='优惠码或者充值卡卡号')
    recharge_amount = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='充值课时')
    incentive_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, verbose_name='充值奖励课时')
    referrer_incentive_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, verbose_name='推荐人奖励课时')
    total_amount = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='总课时')
    referrer_user = models.ForeignKey(UserParentInfo, models.DO_NOTHING, blank=True, null=True, related_name='referrer_recharge_order', verbose_name='推荐人用户标识')
    referrer_username = models.CharField(max_length=63, blank=True, null=True, verbose_name='推荐人用户名')
    currency_id = models.IntegerField(help_text='货币标识')
    currency = models.CharField(max_length=15, help_text='货币名称')
    rate = models.DecimalField(max_digits=18, decimal_places=6, help_text='货币单价')
    origin_total_price = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='原始总金额')
    discount = models.IntegerField(blank=True, null=True, verbose_name='优惠码对应的折扣率')
    save_price = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='节省金额')
    total_price = models.DecimalField(max_digits=18, decimal_places=6, verbose_name='需支付的总金额')
    reference = models.CharField(max_length=255, verbose_name='外部支付订单号，stripe支付为rechargeId')
    status = models.IntegerField(choices=STATUS_CHOICE, default=PAID)
    first_recharge = models.IntegerField(choices=FIRST_RECHARGE_CHOICE, null=True, blank=True, help_text='是否首次充值，0：续费；1：首充')
    pay_type = models.CharField(max_length=31, choices=PAY_STATUS_CHOICE, null=True, blank=True, help_text='支付方式，card、alipay、wechat')
    # create_time = models.DateTimeField(auto_now_add=True)
    # update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()

    def __str__(self):
        return '{}--{}'.format(self.parent_user.username, self.get_status_display())

    class Meta:
        managed = False
        db_table = 'finance_recharge_order'


class Payment(models.Model):

    '''支付表'''
    order = models.ForeignKey(RechargeOrder, help_text='订单表id')
    amount = models.BigIntegerField(help_text='支付金额')
    reference = models.CharField(max_length=63, help_text='支付通道订单id')
    type = models.CharField(max_length=15, help_text='支付方式 card:行卡;alipa:支付宝;wecha:微信')
    status = models.IntegerField(help_text='支付状态 0:待支付;1:支付成功;2:支付失败;3:支付超时;4:退款')
    channel = models.CharField(max_length=31, help_text='支付通道 stripe;paypal')
    mark = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    success_time = models.DateField(null=True, blank=True, help_text='支付成功时间')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'order_id:{}-amount:{}-status:{}'.format(self.order.id, self.amount, self.status)

    class Meta:
        managed = False
        db_table = 'finance_payment'


class Transfer(models.Model):

    '''学生之间课时转让流水记录'''

    amount = models.DecimalField(max_digits=18, decimal_places=6)
    recipient_user = models.ForeignKey(UserParentInfo, models.CASCADE, related_name='recipient', verbose_name='转入者的用户标识')
    transfer_user = models.ForeignKey(UserParentInfo, models.CASCADE, related_name='transfer', verbose_name='转出者的用户标识')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_transfer'


class UserCoupon(models.Model):

    '''学生添加的充值优惠码'''

    NOT_USED = 0
    USED = 1
    EXPIRED = 2  # 过期

    USED_CHOICE = (
        (NOT_USED, 'Not Used'),
        (USED, 'Used'),
        (EXPIRED, 'Expired')
    )

    parent_user = models.ForeignKey(UserParentInfo, models.CASCADE)
    code = models.ForeignKey(CommonCoupon, models.CASCADE, db_column='code', verbose_name='优惠码')
    valid_start_time = models.DateTimeField(verbose_name='有效期开始时间')
    valid_end_time = models.DateTimeField(verbose_name='有效期结束时间')
    discount = models.IntegerField(verbose_name='折扣比例，百分比')
    used = models.IntegerField(choices=USED_CHOICE, verbose_name='是否使用')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_user_coupon'


class StripePayMethodInfo(models.Model):

    '''Stripe支付方式信息表'''

    pm_id = models.CharField(max_length=127, verbose_name='支付方式标识')
    type = models.CharField(max_length=31, verbose_name='支付方式类型，card')
    billing_details_name = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单名称')
    billing_details_phone = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单电话')
    billing_details_email = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单邮箱')
    billing_details_address_country = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单国家')
    billing_details_address_state = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单州')
    billing_details_address_city = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单城市')
    billing_details_address_postal_code = models.CharField(max_length=31, blank=True, null=True, verbose_name='账单邮编')
    card_id = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡标识')
    card_country = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡国家，CN')
    address_state = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡州')
    address_city = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡城市')
    card_brand = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡品牌，mastercard')
    card_address_line1 = models.CharField(max_length=255, blank=True, null=True, verbose_name='卡地址1')
    card_address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='卡地址2')
    address_zip = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡邮编')
    card_exp_year = models.IntegerField(verbose_name='过期年份')
    card_exp_month = models.IntegerField(verbose_name='过期月份')
    card_funding = models.CharField(max_length=31, verbose_name='卡类型，credit')
    card_number = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡号')
    card_last4 = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡号后四位')
    card_cvc = models.CharField(max_length=31, blank=True, null=True, verbose_name='卡校验码')
    customer_id = models.CharField(max_length=127, verbose_name='卡用户标识')
    parent_user = models.ForeignKey(UserParentInfo, models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'finance_stripe_pay_method_info'


# class PaypalIpn(models.Model):
#
#     '''paypal支付表'''
#
#     business = models.CharField(max_length=127)
#     charset = models.CharField(max_length=31)
#     custom = models.CharField(max_length=127)
#     notify_version = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
#     parent_txn_id = models.CharField(max_length=31)
#     receiver_email = models.CharField(max_length=127)
#     receiver_id = models.CharField(max_length=127)
#     residence_country = models.CharField(max_length=15)
#     test_ipn = models.IntegerField()
#     txn_id = models.CharField(max_length=127)
#     txn_type = models.CharField(max_length=127)
#     verify_sign = models.CharField(max_length=127)
#     address_country = models.CharField(max_length=63)
#     address_city = models.CharField(max_length=63)
#     address_country_code = models.CharField(max_length=63)
#     address_name = models.CharField(max_length=127)
#     address_state = models.CharField(max_length=63)
#     address_status = models.CharField(max_length=127)
#     address_street = models.CharField(max_length=127)
#     address_zip = models.CharField(max_length=31)
#     contact_phone = models.CharField(max_length=31)
#     first_name = models.CharField(max_length=31)
#     last_name = models.CharField(max_length=31)
#     payer_business_name = models.CharField(max_length=127)
#     payer_email = models.CharField(max_length=127)
#     payer_id = models.CharField(max_length=15)
#     auth_amount = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
#     auth_exp = models.CharField(max_length=31)
#     auth_id = models.CharField(max_length=31)
#     auth_status = models.CharField(max_length=127)
#     exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     invoice = models.CharField(max_length=127)
#     item_name = models.CharField(max_length=127)
#     item_number = models.CharField(max_length=127)
#     mc_currency = models.CharField(max_length=31)
#     mc_fee = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_gross = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_handling = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_shipping = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     memo = models.CharField(max_length=127)
#     num_cart_items = models.IntegerField(blank=True, null=True)
#     option_name1 = models.CharField(max_length=63)
#     option_name2 = models.CharField(max_length=63)
#     payer_status = models.CharField(max_length=127)
#     payment_date = models.DateTimeField(blank=True, null=True)
#     payment_gross = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     payment_status = models.CharField(max_length=127)
#     payment_type = models.CharField(max_length=127)
#     pending_reason = models.CharField(max_length=127)
#     protection_eligibility = models.CharField(max_length=127)
#     quantity = models.IntegerField(blank=True, null=True)
#     reason_code = models.CharField(max_length=127)
#     remaining_settle = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     settle_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     settle_currency = models.CharField(max_length=31)
#     shipping = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     shipping_method = models.CharField(max_length=127)
#     tax = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     transaction_entity = models.CharField(max_length=127)
#     auction_buyer_id = models.CharField(max_length=63)
#     auction_closing_date = models.DateTimeField(blank=True, null=True)
#     auction_multi_item = models.IntegerField(blank=True, null=True)
#     for_auction = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     amount_per_cycle = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     initial_payment_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     next_payment_date = models.DateTimeField(blank=True, null=True)
#     outstanding_balance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     payment_cycle = models.CharField(max_length=127)
#     period_type = models.CharField(max_length=127)
#     product_name = models.CharField(max_length=127)
#     product_type = models.CharField(max_length=127)
#     profile_status = models.CharField(max_length=127)
#     recurring_payment_id = models.CharField(max_length=127)
#     rp_invoice_id = models.CharField(max_length=127)
#     time_created = models.DateTimeField(blank=True, null=True)
#     amount1 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     amount2 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     amount3 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_amount1 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_amount2 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     mc_amount3 = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     password = models.CharField(max_length=31)
#     period1 = models.CharField(max_length=127)
#     period2 = models.CharField(max_length=127)
#     period3 = models.CharField(max_length=127)
#     reattempt = models.CharField(max_length=15)
#     recur_times = models.IntegerField(blank=True, null=True)
#     recurring = models.CharField(max_length=15)
#     retry_at = models.DateTimeField(blank=True, null=True)
#     subscr_date = models.DateTimeField(blank=True, null=True)
#     subscr_effective = models.DateTimeField(blank=True, null=True)
#     subscr_id = models.CharField(max_length=31)
#     username = models.CharField(max_length=63)
#     case_creation_date = models.DateTimeField(blank=True, null=True)
#     case_id = models.CharField(max_length=127)
#     case_type = models.CharField(max_length=127)
#     receipt_id = models.CharField(max_length=127)
#     currency_code = models.CharField(max_length=31)
#     handling_amount = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
#     transaction_subject = models.CharField(max_length=127)
#     ipaddress = models.CharField(max_length=31, blank=True, null=True)
#     flag = models.IntegerField()
#     flag_code = models.CharField(max_length=15)
#     flag_info = models.CharField(max_length=2047)
#     query = models.CharField(max_length=2047)
#     response = models.CharField(max_length=2047)
#     created_at = models.DateTimeField()
#     updated_at = models.DateTimeField()
#     from_view = models.CharField(max_length=15, blank=True, null=True)
#     mp_id = models.CharField(max_length=127, blank=True, null=True)
#     option_selection1 = models.CharField(max_length=127)
#     option_selection2 = models.CharField(max_length=127)
#
#     class Meta:
#         managed = False
#         db_table = 'finance_paypal_ipn'


class TutorSalary(models.Model):

    PAYMENTED = 1
    UNPAY = 0
    PAY_STATUS = (
        (PAYMENTED, 1),
        (UNPAY, 0)
    )

    tutor_user = models.ForeignKey(TutorInfo)
    lesson_num = models.IntegerField(default=0, verbose_name='本月上课课时')
    base_salary = models.DecimalField(max_digits=18, decimal_places=6, default=0.0, verbose_name='基本工资')
    incentive_salary = models.DecimalField(max_digits=18, decimal_places=6, default=0.0, verbose_name='奖励工资')
    student_absence_salary = models.DecimalField(max_digits=18, decimal_places=6, default=0.0, verbose_name='学生缺席老师奖励工资')
    tutor_absence_salary = models.DecimalField(max_digits=18, decimal_places=6, default=0.0, verbose_name='老师缺席罚金')
    currency = models.CharField(max_length=16)
    data_date = models.CharField(max_length=15, default='', verbose_name='教师工资月份')
    student_num = models.IntegerField(default=0, verbose_name='本月学生数量')
    pay_status = models.BooleanField(choices=PAY_STATUS, default=0)
    pay_user_id = models.IntegerField(null=True, blank=True, verbose_name='付款用户标识')
    order_no = models.CharField(max_length=50, null=True, blank=True, verbose_name='转账流水号')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tutor_user', 'data_date',)
        db_table = 'finance_tutor_salary'


class AccountSubscription(models.Model):

    id = models.BigIntegerField(primary_key=True)
    package = models.ForeignKey(CoursePackage, help_text='课程包')
    start_time = models.DateTimeField(help_text='开始时间')
    end_time = models.DateTimeField(help_text='结束时间')
    limits = models.IntegerField(help_text='课时')
    remaining_limits = models.IntegerField(help_text='剩余课时')
    student_user = models.ForeignKey('student.UserStudentInfo', help_text='学生id')
    reference = models.BigIntegerField(help_text='class_id')
    status = models.IntegerField(help_text='状态 0:正常;1过期')
    state = models.IntegerField(help_text='删除状态 0:正常;1:删除')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_subscription'


class OrderReceipt(models.Model):

    UNKNOW = 0
    SEND_SUCCESS = 1
    SEND_FAIL = 2

    STATUS_CHOICE = (
        (SEND_SUCCESS, 'Send Success'),
        (SEND_FAIL, 'Send Fail')
    )

    DELETED = 1
    NOT_DELETE = 0

    STATU_CHOICE = (
        (DELETED, 'Deleted'),
        (NOT_DELETE, 'Not Delete')
    )

    order = models.ForeignKey(RechargeOrder)
    receipt_email = models.CharField(max_length=200, null=True, blank=True, help_text='用户申请接受收据的邮箱')
    status = models.IntegerField(choices=STATUS_CHOICE, default=UNKNOW, help_text='订单收据状态：1-发送成功；2-发送失败')
    statu = models.IntegerField(choices=STATU_CHOICE, default=NOT_DELETE, help_text='删除状态：0-未删除；1-已删除本条数据')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)