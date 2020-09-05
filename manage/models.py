from django.db import models


class PermissionInfo(models.Model):

    '''权限信息表'''

    MENU = 1
    TAB = 2
    BUTTON = 3

    TYPE_CHOICE = (
        (MENU, 'Menu'),
        (TAB, 'Tab'),
        (BUTTON, 'Button'),
    )

    ACTIVE = 1
    INVALID = 0
    STATUS_CHOICE = (
        (ACTIVE, 'Active'),
        (INVALID, 'Invalid')
    )

    pid = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=63)
    full_code = models.CharField(max_length=511)
    type = models.IntegerField(choices=TYPE_CHOICE, help_text='资源类型，1：菜单；2：Tab页签；3：按钮/选项')
    level = models.IntegerField(default=1, help_text='资源级别')
    name_zh = models.CharField(max_length=63)
    name_en = models.CharField(max_length=63)
    icon = models.CharField(max_length=63, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    api_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE, help_text='菜单状态，0：无效；1：有效')
    order_no = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    class Meta:
        managed = False
        db_table = 'permission_info'


class PostInfo(models.Model):

    '''岗位信息表'''

    POST = 1
    DEPARTMENT = 2
    COMPANY = 3
    TYPE_CHOICE = (
        (POST, 'Post'),
        (DEPARTMENT, 'Department'),
        (COMPANY, 'Company')
    )

    DEPT_POST = 1
    EMPLOYEE_POST = 2

    LEADER_CHOICE = (
        (DEPT_POST, 'Dept Post'),
        (EMPLOYEE_POST, 'Employee Post')
    )

    ACTIVE = 1
    INVALID = 0
    STATUS_CHOICE = (
        (ACTIVE, 'Active'),
        (INVALID, 'Invalid')
    )

    pid = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=63)
    full_code = models.CharField(max_length=511, help_text='层级全路径编码')
    type = models.IntegerField(help_text='类别，1：岗位；2：部门；3：公司')
    leader = models.IntegerField(choices=LEADER_CHOICE, default=EMPLOYEE_POST, help_text='岗位类型，1：管理岗；2：基层员工岗')
    name_zh = models.CharField(max_length=63)
    name_en = models.CharField(max_length=63)
    remark = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE, help_text='菜单状态，0：无效；1：有效')
    order_no = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'post_info'


class RoleInfo(models.Model):

    '''角色信息表'''

    SUPER_MANAGER = 1
    NORMAL_MANAGER = 2

    TYPE_CHOICE = (
        (SUPER_MANAGER, 'Super Manager'),
        (NORMAL_MANAGER, 'Normal Manager')
    )

    ACTIVE = 1
    INVALID = 0
    STATUS_CHOICE = (
        (ACTIVE, 'Active'),
        (INVALID, 'Invalid')
    )

    ADVISER_USER_ID = 3
    XG_USER_ID = 4

    type = models.IntegerField(choices=TYPE_CHOICE, default=NORMAL_MANAGER, help_text='角色类型，1：超级管理员；2：普通用户')
    name_zh = models.CharField(max_length=63)
    name_en = models.CharField(max_length=63)
    remark = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ACTIVE, help_text='菜单状态，0：无效；1：有效')
    order_no = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    permission = models.ManyToManyField(PermissionInfo, null=True, blank=True, through='RolePermission')

    class Meta:
        managed = False
        db_table = 'role_info'


class RolePermission(models.Model):

    '''角色权限关联表'''

    role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE)
    permission = models.ForeignKey(PermissionInfo, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'role_permission'


class UserInfo(models.Model):

    '''用户信息表'''

    MALE = 1
    FEMALE = 2
    UNKNOW = 0

    GENDER_CHOICE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOW, 'UnKnow')
    )

    ENABLE = 1
    FORBIDDEN = 0

    STATUS_CHOICE = (
        (ENABLE, 'Enable'),
        (FORBIDDEN, 'Forbidden')
    )

    code = models.CharField(max_length=63)
    username = models.CharField(unique=True, max_length=63, blank=True, null=True)
    password = models.CharField(max_length=127)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=255, blank=True, null=True)
    name_zh = models.CharField(max_length=63, blank=True, null=True)
    name_en = models.CharField(max_length=63, blank=True, null=True)
    realname = models.CharField(max_length=63, blank=True, null=True, db_column='real_name')
    gender = models.IntegerField(choices=GENDER_CHOICE, default=UNKNOW, blank=True, null=True, help_text='性别，0：未知；1：男；2：女')
    wechat = models.CharField(max_length=63, blank=True, null=True)
    wechat_qrcode = models.CharField(max_length=255, blank=True, null=True)
    whatsapp = models.CharField(max_length=63, blank=True, null=True)
    last_login_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=ENABLE, help_text='用户状态，0：停用；1：启用')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    post = models.ManyToManyField(PostInfo, null=True, blank=True, through='UserPost')
    role = models.ManyToManyField(RoleInfo, null=True, blank=True, through='UserRole')

    class Meta:
        managed = False
        db_table = 'user_info'


class UserPost(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    post = models.ForeignKey(PostInfo, on_delete=models.CASCADE)

    class Meta:
        managed = False
        auto_created = True
        db_table = 'user_post'


class UserRole(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE)

    class Meta:
        managed = False
        auto_created = True
        db_table = 'user_role'
