from rest_framework import serializers
from classroom.models import VirtualclassComment, VirtualclassException
from course.serializers import CourseLessonSerializer
from classroom.models import VirtualclassInfo, ClassType, ClassInfo, ClassMember
import datetime
from django.utils import timezone
from utils import utils
from scheduler.models import ScheduleVirtualclassMember
from tutor.models import TutorInfo
from student.models import UserStudentInfo, UserParentInfo, ExtStudent
from datetime import timedelta
from finance.models import AccountBalance
from django.db.models import Sum
from manage.models import UserInfo


class DeletedBigClassScheduleMemberSerializer(serializers.ListSerializer):

    '''删除 schedule_virtualclass_member中的大班课成员'''

    def to_representation(self, data):
        data = data.filter(class_type_id__in=(ClassType.ONE2ONE, ClassType.SMALLCLASS))
        return super(DeletedBigClassScheduleMemberSerializer, self).to_representation(data)


class DeletedBigClassMemberSerializer(serializers.ListSerializer):

    '''删除classroom_class_member中的大班课成员'''

    def to_representation(self, data):
        data = data.filter(class_field__class_type_id__in=(ClassType.ONE2ONE, ClassType.SMALLCLASS))
        return super(DeletedBigClassMemberSerializer, self).to_representation(data)


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = TutorInfo
        fields = ('id', 'username', 'total_number_of_class', 'real_name', 'identity_name')


class BaseParentSerializer(serializers.ModelSerializer):

    parent_name = serializers.SerializerMethodField()

    def get_parent_name(self, obj):
        return obj.username

    class Meta:
        model = UserParentInfo
        fields = ('id', 'parent_name')


class ParentSerializer(BaseParentSerializer):

    parent_name = serializers.SerializerMethodField()
    sg_balance = serializers.SerializerMethodField()

    def get_sg_balance(self, obj):
        balance = AccountBalance.objects.filter(parent_user_id=obj.id, type=AccountBalance.TOPUP_AMOUNT, account_class=AccountBalance.NORMAL_ACCOUNT).aggregate(sg_balance=Sum('balance'))
        return balance['sg_balance']

    def get_parent_name(self, obj):
        return obj.__str__()

    class Meta(BaseParentSerializer.Meta):

        fields = BaseParentSerializer.Meta.fields + ('sg_balance', 'country_of_residence', 'xg_user_name', 'adviser_user_name')


class BaseStudentSerializer(serializers.ModelSerializer):
    parent_user = ParentSerializer()
    age = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_age(self, obj):
        if obj.birthday:
            return timezone.now().year - obj.birthday.year

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'parent_user', 'real_name', 'gender', 'age', 'create_time')


class BaseScheduleVirtualclassMemberSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()  # 学生姓名
    enter_time = serializers.SerializerMethodField()  # 学生进课堂时间
    leave_time = serializers.SerializerMethodField()  # 学生出课堂时间
    parent_name = serializers.SerializerMethodField()  # 家长用户名
    create_time = serializers.SerializerMethodField()  # 学生加入班级时间

    def get_parent_name(self, obj):
        return obj.student_user.parent_user.username

    def get_student_name(self, obj):
        return obj.student_user.real_name

    def get_enter_time(self, obj):
        if obj.enter_time:
            return utils.datetime_to_str(obj.enter_time)

    def get_leave_time(self, obj):
        if obj.leave_time:
            return utils.datetime_to_str(obj.leave_time)

    class Meta:
        list_serializer_class = DeletedBigClassScheduleMemberSerializer
        model = ScheduleVirtualclassMember
        fields = ('student_name', 'enter_time', 'leave_time', 'parent_name')


class ScheduleVirtualclassMemberSerializer(BaseScheduleVirtualclassMemberSerializer):

    course_adviser = serializers.SerializerMethodField()   # 课程顾问
    learn_manager = serializers.SerializerMethodField()    # 学管
    equipment = serializers.SerializerMethodField()   # 上课设备
    student_user_id = serializers.SerializerMethodField()

    def get_student_user_id(self, obj):
        if obj.student_user_id:
            return str(obj.student_user_id)

    def get_course_adviser(self, obj):
        if obj.student_user:
            if obj.student_user.parent_user.adviser_user_id:
                user_infos = self.context.get('user_infos', {})
                if user_infos:
                    user_info = user_infos.get(obj.student_user.parent_user.adviser_user_id)
                    if user_info:
                        return user_info.realname
                else:
                    user_info = UserInfo.objects.filter(id=obj.student_user.parent_user.adviser_user_id).first()
                    if user_info:
                        return user_info.realname

    def get_learn_manager(self, obj):
        if obj.student_user:
            if obj.student_user.parent_user.xg_user_id:
                user_infos = self.context.get('user_infos', {})
                if user_infos:
                    user_info = user_infos.get(obj.student_user.parent_user.xg_user_id)
                    if user_info:
                        return user_info.realname
                else:
                    user_info = UserInfo.objects.filter(id=obj.student_user.parent_user.xg_user_id).first()
                    if user_info:
                        return user_info.realname

    def get_nationality(self, obj):
        if obj.student_user:
            return obj.student_user.parent_user.nationality

    def get_equipment(self, obj):
        # student_id = obj.student_user_id
        # ext_student = ExtStudent.objects.filter(student_id=student_id).first()
        # if ext_student:
        #     return ext_student.equipment
        return None

    class Meta(BaseScheduleVirtualclassMemberSerializer.Meta):
        fields = BaseScheduleVirtualclassMemberSerializer.Meta.fields + ('student_user_id', 'first_course',
                  'course_adviser', 'learn_manager', 'equipment')


class NewScheduleVirtualclassMemberSerializer(serializers.ModelSerializer):
    course_adviser = serializers.SerializerMethodField()  # 课程顾问
    learn_manager = serializers.SerializerMethodField()  # 学管
    equipment = serializers.SerializerMethodField()  # 上课设备
    student_user_id = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()  # 学生姓名
    enter_time = serializers.SerializerMethodField()  # 学生进课堂时间
    leave_time = serializers.SerializerMethodField()  # 学生出课堂时间
    parent_name = serializers.SerializerMethodField()  # 家长用户名

    def get_parent_name(self, obj):
        return obj.student_user.parent_user.username

    def get_student_name(self, obj):
        return obj.student_user.real_name

    def get_enter_time(self, obj):
        if obj.enter_time:
            return utils.datetime_to_str(obj.enter_time)

    def get_leave_time(self, obj):
        if obj.leave_time:
            return utils.datetime_to_str(obj.leave_time)

    def get_student_user_id(self, obj):
        if obj.student_user_id:
            return str(obj.student_user_id)

    def get_course_adviser(self, obj):
        if obj.student_user:
            if obj.student_user.parent_user.adviser_user_id:
                user_infos = self.context.get('user_infos', {})
                if user_infos:
                    user_info = user_infos.get(obj.student_user.parent_user.adviser_user_id)
                    if user_info:
                        return user_info.realname
                else:
                    user_info = UserInfo.objects.filter(id=obj.student_user.parent_user.adviser_user_id).first()
                    if user_info:
                        return user_info.realname

    def get_learn_manager(self, obj):
        if obj.student_user:
            if obj.student_user.parent_user.xg_user_id:
                user_infos = self.context.get('user_infos', {})
                if user_infos:
                    user_info = user_infos.get(obj.student_user.parent_user.xg_user_id)
                    if user_info:
                        return user_info.realname
                else:
                    user_info = UserInfo.objects.filter(id=obj.student_user.parent_user.xg_user_id).first()
                    if user_info:
                        return user_info.realname

    def get_nationality(self, obj):
        if obj.student_user:
            return obj.student_user.parent_user.nationality

    def get_equipment(self, obj):
        # student_id = obj.student_user_id
        # ext_student = ExtStudent.objects.filter(student_id=student_id).first()
        # if ext_student:
        #     return ext_student.equipment
        return None

    class Meta:
        model = ScheduleVirtualclassMember
        fields = ('student_name', 'enter_time', 'leave_time', 'parent_name',
                  'student_user_id', 'first_course', 'course_adviser', 'learn_manager', 'equipment')


class BaseVirtualclassInfoSerializer(serializers.ModelSerializer):

    start_time = serializers.SerializerMethodField()

    def get_start_time(self, obj):
        return utils.datetime_to_str(obj.start_time)

    class Meta:
        model = VirtualclassInfo
        fields = ('id', 'start_time', 'lesson_id')


class VritualclassInfoSerializer(BaseVirtualclassInfoSerializer):

    class_type = serializers.SerializerMethodField()
    tutor_user = TeacherSerializer()
    tk_class_id = serializers.SerializerMethodField()
    appointment_status = serializers.SerializerMethodField()  # 上课状态
    virtualclass_type = serializers.SerializerMethodField()
    finish_status = serializers.SerializerMethodField()  # 结束状态
    exception_desc = serializers.SerializerMethodField()  # 异常原因
    teacher_start_time = serializers.SerializerMethodField()  # 老师上课时间
    teacher_end_time = serializers.SerializerMethodField()  # 老师结束上课时间
    # examine_status = serializers.SerializerMethodField()  # 审核状态

    def get_teacher_start_time(self, obj):
        actual_start = obj.actual_start_time
        if actual_start:
            return utils.datetime_to_str(actual_start)

    def get_teacher_end_time(self, obj):
        actual_end = obj.actual_end_time
        if actual_end:
            return utils.datetime_to_str(actual_end)

    def get_virtualclass_type(self, obj):
        return obj.virtualclass_type.name

    def get_appointment_status(self, obj):
        status = obj.status
        return status

    def get_tk_class_id(self, obj):
        return obj.tk_class_id

    def get_class_type(self, obj):
        class_type = obj.class_type
        type, type_name = None, None
        if class_type:
            type = class_type.name
            if type == 'one2one':
                type_name = '一对一'
            else:
                type_name = '小班课'
        return {'type': type, 'type_name': type_name}

    def get_finish_status(self, obj):
        end_reason = obj.reason
        if end_reason == 0 and obj.status == VirtualclassInfo.NOT_START:
            now_time = timezone.now()
            if obj.start_time <= now_time + datetime.timedelta(hours=-2):
                end_reason = VirtualclassInfo.CLASS_NOONE
        elif end_reason == 0 and obj.status == VirtualclassInfo.STARTED:
            now_time = timezone.now()
            if obj.start_time <= now_time + datetime.timedelta(hours=-2):
                end_reason = VirtualclassInfo.TUTOR_NOT_FINISH
        return end_reason

    def get_exception_desc(self, obj):
        return obj.remark

    # def get_examine_status(self, obj):
    #     vc_exception = VirtualclassException.objects.filter(virtual_class_id=obj.id).first()
    #     if vc_exception:
    #         return '已审核'
    #     return '未审核'

    class Meta(BaseVirtualclassInfoSerializer.Meta):
        fields = BaseVirtualclassInfoSerializer.Meta.fields + ('tutor_user', 'class_type', 'tk_class_id',
                  'appointment_status', 'virtualclass_type', 'finish_status', 'exception_desc',
                  'teacher_start_time', 'teacher_end_time', 'absent_tutor_user_id')


class ClassInfoSerializer(serializers.ModelSerializer):

    # leader_user = LeaderUserSerializer()
    # creator_user = LeaderUserSerializer()
    class_member = serializers.SerializerMethodField()
    # first_course_info = serializers.SerializerMethodField()  # 第一次课信息
    future_class_sum = serializers.SerializerMethodField()  # 待上课程数
    create_time = serializers.SerializerMethodField()  # 创建时间
    # appointment_num = serializers.SerializerMethodField()  # 约课数量
    finish_num = serializers.SerializerMethodField()  # 已完成课时
    actual_student_num = serializers.SerializerMethodField()  # 实际上课人次
    have_student_num = serializers.SerializerMethodField()  # 应到上课人次
    tutor_name = serializers.SerializerMethodField()  # 待上课老师
    next_start_time = serializers.SerializerMethodField()  # 下次上课时间

    def get_next_start_time(self, obj):
        if obj.next_start_time:
            return utils.datetime_to_str(obj.next_start_time)

    def get_tutor_name(self, obj):
        tutor_names = VirtualclassInfo.objects.filter(class_field=obj, status=VirtualclassInfo.NOT_START).all().values('tutor_user__real_name', 'tutor_user__identity_name').distinct()
        return tutor_names

    def get_actual_student_num(self, obj):
        return obj.actual_student_num

    def get_have_student_num(self, obj):
        return obj.have_student_num

    def get_finish_num(self, obj):
        return obj.finish_num

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_future_class_sum(self, obj):
        return obj.future_class_sum

    # def get_first_course_info(self, obj):
    #     virtuaclass_info = VirtualclassInfo.objects.filter(class_field=obj, first_course=1).first()
    #     if not virtuaclass_info:
    #         return None
    #     tutor = virtuaclass_info.tutor_user
    #     return {
    #         'start_time': utils.datetime_to_str(virtuaclass_info.start_time),
    #         # 'start_time': virtuaclass_info.start_time,
    #         'tutor_name': tutor.real_name
    #     }

    def get_class_member(self, obj):
        if obj.class_type_id == ClassType.BIGCLASS:
            return []
        # members = obj.class_member.filter(role=ClassMember.QUITED).all()
        members = ClassMember.objects.filter(class_field=obj, role__in=(ClassMember.MEMBER, ClassMember.MONITOR)).select_related('student_user').select_related('student_user__parent_user').all().only(
            'id', 'student_user__id', 'student_user_id', 'student_user__real_name',
            'student_user__parent_user__adviser_user_id', 'student_user__parent_user__xg_user_id'
        )
        result = []
        for member in members:
            adviser_user_name = None
            xg_user_name = None
            adviser_user_id = member.student_user.parent_user.adviser_user_id
            if adviser_user_id:
                adviser_user = UserInfo.objects.filter(id=adviser_user_id).first()
                if adviser_user:
                    adviser_user_name = adviser_user.realname
            xg_user_id = member.student_user.parent_user.xg_user_id
            if xg_user_id:
                xg_user = UserInfo.objects.filter(id=xg_user_id).first()
                if xg_user:
                    xg_user_name = xg_user.realname
            result.append({
                'id': member.student_user_id,
                'real_name': member.student_user.real_name,
                'adviser_user_name': adviser_user_name,
                'xg_user_name': xg_user_name
            })
        return result

    class Meta:
        model = ClassInfo
        fields = ('id', 'class_no', 'class_member', 'future_class_sum', 'next_start_time',
                  'user_max', 'user_num', 'class_name_zh', 'class_name', 'course_edition_id',
                  'course_level', 'lesson_no', 'create_time', 'finish_num', 'tutor_name',
                  'actual_student_num', 'have_student_num', 'create_user_id', 'create_user_name')


class SmallClassInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassInfo
        fields = ('id', 'class_no', 'class_name_zh', 'class_name', 'create_user_name')


class SmallClassVirtualclassSerializer(BaseVirtualclassInfoSerializer):

    tutor_user = TeacherSerializer()
    # virtual_class_member = ScheduleVirtualclassMemberSerializer(many=True)
    class_field = SmallClassInfoSerializer()

    def get_start_time(self, obj):
        return utils.datetime_to_str(obj.start_time)

    def get_course_info(self, obj):
        course_info = self.context.get('course_info')
        return course_info.get(obj.lesson_id)

    class Meta(BaseVirtualclassInfoSerializer.Meta):
        fields = BaseVirtualclassInfoSerializer.Meta.fields + ('class_field', 'tutor_user')


class SmallclassVirtualclassMemberSerializer(BaseScheduleVirtualclassMemberSerializer):

    status = serializers.SerializerMethodField()
    adviser_user_name = serializers.SerializerMethodField()
    xg_user_name = serializers.SerializerMethodField()

    def get_adviser_user_name(self, obj):
        return obj.student_user.parent_user.adviser_user_name

    def get_xg_user_name(self, obj):
        return obj.student_user.parent_user.xg_user_name

    def get_status(self, obj):
        if obj.virtual_class.status in (VirtualclassInfo.STARTED, VirtualclassInfo.NOT_START):
            return 0
        start_time = obj.start_time
        end_time = obj.virtual_class.end_time
        if not obj.enter_time:
            return 1   # 缺席
        elif start_time < obj.enter_time + timedelta(minutes=-10):
            return 2  # 迟到
        elif not obj.leave_time or end_time > obj.leave_time:
            return 3  # 早退
        return 0

    class Meta(BaseScheduleVirtualclassMemberSerializer.Meta):
        fields = BaseScheduleVirtualclassMemberSerializer.Meta.fields + ('status', 'adviser_user_name', 'xg_user_name')


class SmallClassVirtualclassInfoSerializer(SmallClassVirtualclassSerializer):

    virtual_class_member = SmallclassVirtualclassMemberSerializer(many=True)
    class_times = serializers.SerializerMethodField()
    appointment_count = serializers.SerializerMethodField()

    def get_appointment_count(self, obj):
        return obj.appointment_count

    def get_class_times(self, obj):
        return obj.class_times

    class Meta(SmallClassVirtualclassSerializer.Meta):

        fields = SmallClassVirtualclassSerializer.Meta.fields + ('virtual_class_member', 'status', 'class_times', 'appointment_count')


# class SmallClassVirtualclassDetailSerializer(SmallClassVirtualclassSerializer):
#
#     tutor_user = TeacherSerializer()
#     course_info = serializers.SerializerMethodField()
#     virtual_class_member = ScheduleVirtualclassMemberSerializer(many=True)
#
#     def get_course_info(self, obj):
#         course_lesson = obj.lesson
#         if course_lesson:
#             return {
#                 'course_name': course_lesson.course.course_name,
#                 'course_level': course_lesson.course.course_level,
#                 'course_edition_name': course_lesson.course.course_edition.edition_name,
#                 'lesson_no': course_lesson.lesson_no,
#                 'unit_no': course_lesson.unit_no
#             }
#         class_info = obj.class_field
#         return {
#             'course_name': class_info.course.course_name,
#             'course_level': class_info.course_level,
#             'course_edition_name': class_info.course_edition.edition_name,
#             'lesson_no': class_info.lesson_no,
#             'unit_no': course_lesson.unit_no
#         }
#
#     class Meta(SmallClassVirtualclassSerializer.Meta):
#         fields = SmallClassVirtualclassSerializer.Meta.fields + ('tutor_user', 'course_info', 'virtual_class_member')


class MatchTutorInfoSerializer(serializers.ModelSerializer):

    appointment_status = serializers.SerializerMethodField()  # 发布课时匹配情况
    student_count = serializers.SerializerMethodField()  # 当前学生数量
    status = serializers.SerializerMethodField()  # 老师状态
    full_work = serializers.SerializerMethodField()  # 是否是全职老师

    def get_full_work(self, obj):
        return obj.full_work

    def get_status(self, obj):
        if obj.status == TutorInfo.ACTIVE:
            if obj.working == TutorInfo.WORKING:
                if obj.hide == TutorInfo.HIDDEN:
                    tutor_status = 1  # 仅老生可见
                else:
                    tutor_status = 0  # 上岗
            else:
                tutor_status = 2  # 下岗
        else:
            tutor_status = 3  # 未激活
        return tutor_status

    def get_appointment_status(self, obj):
        tutor_publish_dict = self.context.get('tutor_publish_dict', {})
        return tutor_publish_dict.get(obj.id, None)

    def get_student_count(self, obj):
        return obj.student_count

    class Meta:
        model = TutorInfo
        fields = ('id', 'username', 'real_name', 'identity_name', 'phone', 'appointment_status',
                  'student_count', 'status', 'full_work')


class StudentSerializer(serializers.ModelSerializer):

    parent_user = BaseParentSerializer()

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'parent_user', 'real_name')


class CommentSerializer(serializers.ModelSerializer):

    virtual_class = BaseVirtualclassInfoSerializer()
    create_time = serializers.SerializerMethodField()
    tutor_user = TeacherSerializer()
    student_user = StudentSerializer()

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    class Meta:
        model = VirtualclassComment
        fields = ('id', 'create_time', 'tutor_user', 'student_user', 'virtual_class', 'difficult_level', 'suggestion')
