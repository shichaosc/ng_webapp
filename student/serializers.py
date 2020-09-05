from rest_framework import serializers
from django.contrib.auth.models import User
from utils import utils
from student.config import REGISTER, RECHARGED, APPOINTMENT, AUDITED
import datetime
from student.models import UserStudentInfo, UserParentInfo, StudentRemark, ExtStudent, UserIp
from classroom.models import VirtualclassInfo, ClassMember
from course.serializers import CourseEditionSerializer
from django.utils import timezone
from django.db.models import Sum
from manage.models import RoleInfo, UserInfo
from finance.models import AccountBalance


class BaseStudentSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    real_name = serializers.CharField(read_only=True)
    # virtual_class_sum = serializers.SerializerMethodField(read_only=True)  # 已上课程数
    # course_info = serializers.SerializerMethodField(read_only=True)  # 等级
    course_adviser = serializers.SerializerMethodField(read_only=True)  # 课程顾问
    learn_manager = serializers.SerializerMethodField(read_only=True)   # 学管
    # balance = serializers.SerializerMethodField(read_only=True)   # 账户余额
    parent_name = serializers.SerializerMethodField(read_only=True)  # 家长用户名
    lesson_id = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(serializers.Serializer, self).__init__(*args, **kwargs)
        self.all_manage_users = self.struct_user_info()

    def struct_user_info(self):
        users = UserInfo.objects.all().only('id', 'username', 'realname')
        result = {}
        for user in users:
            result[user.id] = user
        return result

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('lesson').select_related('lesson__course').select_related('lesson__course__course_edition').select_related('parent_user').only('id', 'real_name', 'create_time', 'lesson__id', 'lesson__lesson_no', 'lesson__course__course_level', 'lesson__course__course_name', 'lesson__course__course_edition__edition_name', 'parent_user__adviser_user_id', 'parent_user__xg_user_id', 'parent_user__username', 'parent_user__email', 'parent_user__phone', 'parent_user__code', 'parent_user__referrer_user_id')
        return queryset

    def get_id(self, obj):
        return obj.id

    # def get_virtual_class_sum(self, obj):
    #     if obj.virtual_class_sum:
    #         return obj.virtual_class_sum
    #     return 0

    def get_parent_name(self, obj):
        return obj.parent_user.username

    # def get_balance(self, obj):
    #     account_balance = AccountBalance.objects.filter(parent_user_id=obj.parent_user_id, account_class=AccountBalance.NORMAL_ACCOUNT).aggregate(balance=Sum('balance'))
    #     return account_balance['balance']

    def get_id(self, obj):
        return str(obj.id)

    def get_course_adviser(self, obj):
        if obj.parent_user.adviser_user_id:
            user_info = self.all_manage_users.get(obj.parent_user.adviser_user_id)
            if user_info:
                return {
                    'id': user_info.id,
                    'name': user_info.realname
                }

    def get_learn_manager(self, obj):
        if obj.parent_user.xg_user_id:
            user_info = self.all_manage_users.get(obj.parent_user.xg_user_id)
            if user_info:
                return {
                    'id': user_info.id,
                    'name': user_info.realname
                }
    def get_lesson_id(self, obj):
        return obj.lesson_id

    # def get_course_info(self, obj):
    #     lesson = obj.lesson
    #     if lesson:
    #         lesson_no = obj.lesson.lesson_no
    #         course_name = obj.lesson.course.course_name
    #         course_level = obj.lesson.course.course_level
    #         course_edition_name = obj.lesson.course.course_edition.edition_name
    #         return {
    #             'course_name': course_name,
    #             'course_level': course_level,
    #             'course_edition_name': course_edition_name,
    #             'lesson_no': lesson_no
    #         }
    #     return None

    # class Meta:
    #     model = UserStudentInfo
    #     fields = ('id', 'real_name', 'virtual_class_sum', 'course_info', 'course_adviser', 'learn_manager',
    #                'balance', 'parent_name')


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    def get_last_login(self, obj):
        if obj.last_login:
            return utils.datetime_to_str(obj.last_login)

    def get_date_joined(self, obj):
        if obj.date_joined:
            return utils.datetime_to_str(obj.date_joined)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'last_login')


class StudentIpSerializer(BaseStudentSerializer):

    '''新增了用户所在地区'''
    student_area = serializers.SerializerMethodField(read_only=True)
    def get_student_area(self, obj):
        # user_ip = UserIp.objects.filter(parent_user_id=obj.parent_user_id).only('country').first()
        # if user_ip:
        #     return user_ip.country
        return ''

    # class Meta(BaseStudentSerializer.Meta):
    #     fields = BaseStudentSerializer.Meta.fields + ('student_area', )


class StudentSerializer(StudentIpSerializer):

    user_status = serializers.SerializerMethodField(read_only=True)
    # smallclass_count = serializers.SerializerMethodField(read_only=True)  # 小班课余额
    student_source = serializers.SerializerMethodField(read_only=True)  # 学生来源
    create_time = serializers.SerializerMethodField(read_only=True)  # 创建时间
    parent_user_id = serializers.SerializerMethodField(read_only=True)  # 家长id

    def get_parent_user_id(self, obj):
        return obj.parent_user_id

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_user_status(self, obj):
        student_status = self.context.get('student_status')
        if student_status == RECHARGED:
            return '已充值'
        elif student_status == REGISTER:
            return '已注册'
        elif student_status == AUDITED:
            return '已试听'
        elif student_status == APPOINTMENT:
            return '已预约试听'

        if obj.recharge_sum and obj.recharge_sum > 1:
            return '已充值'
        elif obj.first_course == 0:
            return '已试听'
        else:
            vc = VirtualclassInfo.objects.filter(virtual_class_member__student_user__id=obj.id, status__in=(VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED), class_type_id__in=(1,2)).only('id').first()
            if vc:
                return '已预约试听'
        return '已注册'

    def get_student_source(self, obj):
        if obj.parent_user.code:
            return '城市合伙人'
        elif obj.parent_user.referrer_user_id:
            return '转介绍'
        return '直接用户'


class ParentBaseInfoSerializer(serializers.ModelSerializer):

    login_time = serializers.SerializerMethodField()
    course_adviser = serializers.SerializerMethodField()
    learn_manager = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    small_class_balance = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()  # 总账户余额

    def get_balance(self, obj):
        balance = AccountBalance.objects.filter(parent_user_id=obj.id,
                                                account_class=AccountBalance.NORMAL_ACCOUNT).aggregate(
            balance=Sum('balance'))
        return balance['balance']

    def get_small_class_balance(self, obj):
        balance = AccountBalance.objects.filter(parent_user_id=obj.id, account_class=AccountBalance.PRIVATE_ACCOUNT).aggregate(sg_balance=Sum('balance'))
        return balance['sg_balance']

    def get_course_adviser(self, obj):
        if obj.adviser_user_id:
            user_info = UserInfo.objects.filter(id=obj.adviser_user_id).first()
            if user_info:
                return user_info.realname

    def get_learn_manager(self, obj):
        if obj.xg_user_id:
            user_info = UserInfo.objects.filter(id=obj.xg_user_id).first()
            if user_info:
                return user_info.realname

    def get_login_time(self, obj):
        if obj.login_time:
            return utils.datetime_to_str(obj.login_time)

    def get_source(self, obj):
        if obj.code:
            return '城市合伙人'
        elif obj.referrer_user_id:
            return '转介绍'
        else:
            return '直接用户'

    class Meta:
        model = UserParentInfo
        fields = ('id', 'username', 'email', 'phone', 'nationality', 'currency', 'balance', 'login_tz',
                  'referrer_user_name', 'referrer_user_identify', 'login_time', 'wechat', 'whatsapp', 'course_adviser',
                  'learn_manager', 'source', 'small_class_balance', 'country_of_residence')


class ParentInfoSerializer(serializers.ModelSerializer):

    login_time = serializers.SerializerMethodField()
    course_adviser = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    # small_class_balance = serializers.SerializerMethodField()
    # balance = serializers.SerializerMethodField()  # 总账户余额
    #
    # def get_balance(self, obj):
    #     balance = AccountBalance.objects.filter(parent_user_id=obj.id,
    #                                             account_class=AccountBalance.NORMAL_ACCOUNT).aggregate(
    #         balance=Sum('balance'))
    #     return balance['balance']
    #
    # def get_small_class_balance(self, obj):
    #     balance = AccountBalance.objects.filter(parent_user_id=obj.id, account_class=AccountBalance.PRIVATE_ACCOUNT).aggregate(sg_balance=Sum('balance'))
    #     return balance['sg_balance']

    def get_course_adviser(self, obj):
        if obj.adviser_user_id:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(obj.adviser_user_id)
            if user_info:
                return user_info.realname

    def get_login_time(self, obj):
        if obj.login_time:
            return utils.datetime_to_str(obj.login_time)

    def get_source(self, obj):
        if obj.code:
            return '城市合伙人'
        elif obj.referrer_user_id:
            return '转介绍'
        else:
            return '直接用户'

    class Meta:
        model = UserParentInfo
        fields = ('id', 'username', 'email', 'phone', 'nationality', 'currency', 'login_tz',
                  'referrer_user_name', 'referrer_user_identify', 'login_time', 'wechat', 'whatsapp', 'course_adviser',
                  'source', 'country_of_residence')


class StudentInfoSerializer(serializers.ModelSerializer):

    # id = serializers.SerializerMethodField()
    parent_user = ParentBaseInfoSerializer()
    gender = serializers.SerializerMethodField()
    register_date = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    course_edition = CourseEditionSerializer()
    course_adviser = serializers.SerializerMethodField()
    learn_manager = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_course_adviser(self, obj):
        if obj.parent_user.adviser_user_id:
            user_info = UserInfo.objects.filter(id=obj.parent_user.adviser_user_id).first()
            if user_info:
                return user_info.realname

    def get_learn_manager(self, obj):
        if obj.parent_user.xg_user_id:
            user_info = UserInfo.objects.filter(id=obj.parent_user.xg_user_id).first()
            if user_info:
                return user_info.realname

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_register_date(self, obj):
        if obj.create_time:
            return utils.datetime_to_str(obj.create_time)

    def get_birthday(self, obj):
        if obj.birthday:
            return utils.datetime_to_str(obj.birthday)

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'real_name', 'parent_user', 'gender', 'birthday',
                  'register_date', 'course_edition', 'course_adviser', 'learn_manager', 'create_time')


class OldStudentSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    real_name = serializers.CharField(read_only=True)
    # course_adviser = serializers.SerializerMethodField(read_only=True)  # 课程顾问
    # last_info = serializers.SerializerMethodField(read_only=True)  # 最近上课时间, 最近上课老师
    # next_info = serializers.SerializerMethodField(read_only=True)  # 下次上课时间, 下次上课老师
    last_remark = serializers.SerializerMethodField(read_only=True)  # 距离上次备注
    # lesson_sum = serializers.SerializerMethodField(read_only=True)  # 本月上课次数
    parent_user = ParentInfoSerializer(read_only=True)
    create_time = serializers.SerializerMethodField(read_only=True)  # 创建时间
    student_area = serializers.SerializerMethodField(read_only=True)
    # virtual_class_sum = serializers.SerializerMethodField(read_only=True)  # 已上课程数
    lesson_id = serializers.SerializerMethodField(read_only=True)  # 等级
    learn_manager = serializers.SerializerMethodField()

    def get_learn_manager(self, obj):

        if obj.parent_user.xg_user_id:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(obj.parent_user.xg_user_id)
            if user_info:
                return {
                    'id': user_info.id,
                    'name': user_info.realname
                }

    def get_id(self, obj):
        return obj.id

    def get_real_name(self, obj):
        return obj.real_name

    def get_lesson_id(self, obj):
        return obj.lesson_id

    def get_student_area(self, obj):
        user_ip = UserIp.objects.filter(parent_user_id=obj.parent_user_id).only('country').first()
        if user_ip:
            return user_ip.country
        return ''

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_last_remark(self, obj):
        return None

    # class Meta(StudentIpSerializer.Meta):
    #     fields = StudentIpSerializer.Meta.fields + ('last_info', 'next_info', 'last_remark', 'lesson_sum', 'parent_user', 'create_time')
    #     # read_only_fields = fields


class ExtStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtStudent
        fields = ('id', 'class_year', 'parental_expectation', 'literacy', 'write_amount', 'pinyin',
                  'chinese_experience', 'language_environment', 'gender', 'equipment', 'listen_speak_ability')


class ExtStudentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtStudent


class RemarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentRemark
        fields = '__all__'


class RemarkRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoleInfo
        fields = ('id', 'name_zh')


class RemarkUserSerializer(serializers.ModelSerializer):

    role = RemarkRoleSerializer(many=True)

    class Meta:
        model = UserInfo
        fields = ('username', 'role')


class RemarkListSerializer(serializers.ModelSerializer):

    user = RemarkUserSerializer()
    create_time = serializers.SerializerMethodField()

    def get_create_time(self, obj):
        if obj.create_time:
            return utils.datetime_to_str(obj.create_time)
        return None

    class Meta:
        model = StudentRemark
        fields = ('user', 'create_time', 'content')


class RechargeStudentUser(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return str(obj.id)

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'real_name')


class RechargeParentUser(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    children = RechargeStudentUser(many=True)

    def get_id(self, obj):
        return str(obj.id)

    def get_parent_name(self, obj):
        return obj.__str__()

    class Meta:
        model = UserParentInfo
        fields = ('id', 'parent_name', 'children', 'adviser_user_name', 'xg_user_name')


class WarnStudentSerializer(BaseStudentSerializer):

    recharge_sum = serializers.SerializerMethodField(read_only=True)  # 累计充值课时
    last_info = serializers.SerializerMethodField(read_only=True)  # 最近上课时间, 最近上课老师
    recharge_count = serializers.SerializerMethodField(read_only=True)  # 充值次数
    last_recharge_time = serializers.SerializerMethodField(read_only=True)  # 最近充值时间
    create_time = serializers.SerializerMethodField(read_only=True)  # 注册时间
    parent_user_id = serializers.SerializerMethodField(read_only=True)  # 注册时间

    def get_parent_user_id(self, obj):
        return obj.parent_user_id

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_last_recharge_time(self, obj):
        if obj.last_recharge_time:
            return obj.last_recharge_time

    def get_recharge_count(self, obj):
        return obj.recharge_count

    def get_last_info (self, obj):
        last_vc = VirtualclassInfo.objects.filter(virtual_class_member__student_user_id=obj.id, status=VirtualclassInfo.FINISH_NOMAL).select_related('tutor_user').order_by('-start_time').only('id', 'start_time', 'tutor_user__username', 'tutor_user__real_name', 'tutor_user__identity_name').first()
        if not last_vc:
            return None
        return {
            'last_teacher': last_vc.tutor_user.username,
            'last_teacher_real_name': last_vc.tutor_user.real_name,
            'last_teacher_identity_name': last_vc.tutor_user.identity_name,
            'last_attend_time': utils.datetime_to_str(last_vc.start_time)
        }

    def get_recharge_sum(self, obj):
        return obj.recharge_sum


class SmallClassParentSerializer(serializers.ModelSerializer):

    parent_name = serializers.SerializerMethodField()
    # xg_user_name = serializers.SerializerMethodField()
    # adviser_user_name = serializers.SerializerMethodField()

    def get_adviser_user_name(self, obj):
        if obj.adviser_user_id:
            user_info = UserInfo.objects.filter(id=obj.adviser_user_id).first()
            if user_info:
                return user_info.realname

    def get_xg_user_name(self, obj):
        if obj.xg_user_id:
            user_info = UserInfo.objects.filter(id=obj.xg_user_id).first()
            if user_info:
                return user_info.realname

    def get_parent_name(self, obj):
        return obj.username

    class Meta:
        model = UserParentInfo
        fields = ('id', 'parent_name', 'country_of_residence', 'xg_user_id', 'adviser_user_id')


class SmallClassStudentSerializer(serializers.ModelSerializer):

    parent_user = SmallClassParentSerializer()
    age = serializers.SerializerMethodField()  # 年龄
    class_fields_list = serializers.SerializerMethodField()  # 学生加入的班级列表

    def get_class_fields_list(self, obj):
        class_nos = ClassMember.objects.filter(student_user_id=obj.id, role__in=(ClassMember.MONITOR, ClassMember.MEMBER)).all().values('class_field__class_no')
        result = []
        for class_no in class_nos:
            result.append(class_no['class_field__class_no'])
        return result

    def get_age(self, obj):
        if obj.birthday:
            return timezone.now().year - obj.birthday.year

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'real_name', 'parent_user', 'age', 'gender', 'class_fields_list')
