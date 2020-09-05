from django.db import models


class UserAmbassadorInfo(models.Model):

    '''城市合伙人用户信息'''
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

    MALE = 1
    FEMALE = 2
    UNKNOWN = 0
    GENDER_CHOICE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Unknown')
    )

    PAYPAL = 2
    DEBIT = 2
    ACCOUNT_CHOICE = (
        (PAYPAL, 'PayPal'),
        (DEBIT, 'Debit')
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

    id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOICE, default=AMBASSADOR)
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
    currency = models.CharField(max_length=15, blank=True, null=True, verbose_name='货币名称')
    language = models.CharField(choices=LANGRANGE_CHOICE, default=EN, max_length=31, blank=True, null=True)
    whatsapp = models.CharField(max_length=255, blank=True, null=True)
    wechat = models.CharField(max_length=255, blank=True, null=True)
    phone_country_code = models.CharField(max_length=15, blank=True, null=True, verbose_name='电话国家码')
    occupation = models.CharField(max_length=32, blank=True, null=True, verbose_name='职业')
    default_account = models.IntegerField(choices=ACCOUNT_CHOICE, default=PAYPAL, verbose_name='默认账号')
    paypal_email = models.CharField(max_length=255, blank=True, null=True, verbose_name='paypal账号')
    swift_code = models.CharField(max_length=15, blank=True, null=True, verbose_name='银行识别码')
    iban = models.CharField(max_length=31, blank=True, null=True, verbose_name='国际银行账户号码')
    benificiary_name = models.CharField(max_length=63, blank=True, null=True, verbose_name='受益人名称')
    benificiary_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='受益人地址')
    benificiary_bank_name = models.CharField(max_length=63, blank=True, null=True, verbose_name='受益人银行账号名称')
    benificiary_bank_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='受益人银行账号地址')
    benificiary_account_number = models.CharField(max_length=31, blank=True, null=True, verbose_name='受益人账号')
    code = models.CharField(unique=True, max_length=31, verbose_name='推广码，标识城市合伙人身份')
    last_login_tz = models.CharField(max_length=31, blank=True, null=True)
    last_login_time = models.DateTimeField(blank=True, null=True)
    login_tz = models.CharField(max_length=31, blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
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
        db_table = 'user_ambassador_info'
