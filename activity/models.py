from django.db import models
from student.models import UserParentInfo


class ActivityBannerInfo(models.Model):

    ''''活动页类型，1：APP页面；2：H5页面，默认2','''
    APP_ROUTE = 1
    H5_ROUTE = 2
    ROUTE_CHOICE = (
        (APP_ROUTE, 'App Route'),
        (H5_ROUTE, 'H5 Route')
    )

    DISPLAY = 1
    HIDDEN = 0

    STATUS_CHOICE = (
        (DISPLAY, 'Display'),
        (HIDDEN, 'Hidden')
    )

    name = models.CharField(max_length=127)
    picture_url = models.CharField(max_length=255)
    route_type = models.IntegerField(choices=ROUTE_CHOICE, default=H5_ROUTE)
    route_url = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICE, default=HIDDEN, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'activity_banner_info'

    def __str__(self):
        return "{}-{}-{}".format(self.name, self.get_route_type_display(), self.get_status_display())


class ActivityMessageInfo(models.Model):
    ''''
    消息子类型：
    101：课程预约成功提醒（单次预约）；
    102：课程预约成功提醒（多次预约）；
    103：课程取消成功提醒（取消单次）；
    104：课程取消成功提醒（取消多次）；
    105：预占的时间自动预约提醒（自动预约单次）；
    106：预占的时间自动预约提醒（自动预约多次）；
    107：欠费课程被取消提醒（单次课）；
    108：欠费课程被取消提醒（多次课）；
    109：老师已提交课堂评价；
    120：作业已批改提醒；
    301：APP升级通知；
    302：充值成功通知；
    303：余额不足通知；
    304：缺席扣除课时费通知'

    通知消息类型:
    1：课程提醒；
    2：活动通知；
    3：系统通知
    '''

    COURSE_MSG = 1
    ACTIVITY_MSG = 2
    SYSTEM_MSG = 3

    SUB_SINGLE_SUBSCRIBE = 101
    SUB_MANY_SUBSCRIBE = 102
    SUB_SINGLE_CANCEL = 103
    SUB_MANY_CANCEL = 104
    SUB_SINGLE_OCCUPATION = 105
    SUB_MANY_OCCUPATION = 106
    SUB_NOMONEY_SINGEL_CANCEL = 107
    SUB_NOMONEY_MANY_CANCEL = 108
    SUB_COMMIT_ASSESSMENT = 109
    SUB_COMMENTED_HOMEWORK = 120
    SUB_APP_UPGRADE = 301
    SUB_RECHARGE_SUCCESS = 302
    SUB_NO_ENOUGH_BALANCE = 303
    SUB_ABSENCE_PENALTY = 304

    SUB_CATEGORY_CHOICE = (
        (SUB_SINGLE_SUBSCRIBE, '单次约课成功提醒'),
        (SUB_MANY_SUBSCRIBE, '多次约课成功提醒'),
        (SUB_SINGLE_CANCEL, '成功单次取消约课提醒'),
        (SUB_MANY_CANCEL, '成功多次取消约课成功提醒'),
        (SUB_SINGLE_OCCUPATION, '预占的时间自动预约提醒（自动预约单次）'),
        (SUB_MANY_OCCUPATION, '预占的时间自动预约提醒（自动预约多次）'),
        (SUB_NOMONEY_SINGEL_CANCEL, '欠费课程被取消提醒（单次课)'),
        (SUB_NOMONEY_MANY_CANCEL, '欠费课程被取消提醒（多次课）'),
        (SUB_COMMIT_ASSESSMENT, '老师已提交课堂评价'),
        (SUB_COMMENTED_HOMEWORK, '作业已批改提醒'),
        (SUB_APP_UPGRADE, 'APP升级通知'),
        (SUB_RECHARGE_SUCCESS, '充值成功通知'),
        (SUB_NO_ENOUGH_BALANCE, '余额不足通知'),
        (SUB_ABSENCE_PENALTY, '缺席扣除课时费通知'),
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

    role = models.IntegerField(choices=ROLE_CHOICE, blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    sub_category = models.IntegerField(choices=SUB_CATEGORY_CHOICE)
    detail = models.CharField(max_length=4095)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_sub_category_display()

    class Meta:
        managed = False
        db_table = 'activity_message_info'


class ActivityGroupInfo(models.Model):

    CLOSED = 0
    ACTIVE = 1
    GROUP_SUCCESS = 2
    PAIED_BONUS = 3

    STATUS_CHOICE = (
        (CLOSED, 'Closed'),
        (ACTIVE, 'Active'),
        (GROUP_SUCCESS, 'Group Success'),
        (PAIED_BONUS, 'Paied Bonus')
    )

    GRANT = 1
    NO_GRANT = 0

    PAY_CHOICE = (
        (GRANT, 'Grant'),
        (NO_GRANT, 'No Grant')
    )

    group_no = models.CharField(max_length=255, blank=True)
    group_url = models.CharField(max_length=255, default='', blank=True)
    user_id = models.IntegerField(help_text='创建人')
    username = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE, help_text='状态，0：关闭；1：启用；2：拼团成功；3：奖励已发放')
    success_time = models.DateTimeField(blank=True, null=True, help_text='拼团成功时间')
    grant_award = models.IntegerField(choices=PAY_CHOICE, default=NO_GRANT, help_text='是否发放', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity_group_info'


class ActivityGroupRecharge(models.Model):

    group = models.ForeignKey(ActivityGroupInfo, on_delete=models.CASCADE, related_name='group_member')
    parent_user = models.ForeignKey(UserParentInfo, on_delete=models.CASCADE)
    recharge_amount = models.IntegerField(help_text='充值课时')
    bonus_amount = models.IntegerField(help_text='奖励课时')
    order_no = models.CharField(max_length=63, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity_group_recharge'
