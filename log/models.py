from django.db import models
from manage.models import UserInfo

class ManagerLog(models.Model):

    SUCCESS = 1
    FAIL = 0
    LOG_STATUS = (
        (SUCCESS, 'success'),
        (FAIL, 'fial'),
    )
    OPERATE_LOG = 2
    LOGIN_LOG = 1
    LOG_TYPE = (
        (LOGIN_LOG, 'login'),
        (OPERATE_LOG, 'operate'),
    )

    user = models.ForeignKey(UserInfo, on_delete=models.Case)
    operation = models.CharField(max_length=50, verbose_name='行为')
    operate_type = models.CharField(max_length=50, verbose_name='操作对象类型')
    operate_name = models.CharField(max_length=50, verbose_name='操作对象名称')
    create_time = models.DateTimeField(auto_now_add=True)  # 会在model对象第一次被创建时，将字段的值设置为创建时的时间，以后修改对象时，字段的值不会再更新
    client_ip = models.CharField(max_length=50, default='')
    status = models.BooleanField(choices=LOG_STATUS, default=SUCCESS, verbose_name='登陆 1:success, 0:fail')
    type = models.SmallIntegerField(choices=LOG_TYPE, default=OPERATE_LOG, verbose_name='日志类型 1:登陆日志, 2:操作日志')

    class Meta:
        db_table = 'manager_managerlog'
