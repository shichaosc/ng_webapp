from rest_framework import serializers
from classroom.models import VirtualclassInfo, ClassMember, ClassInfo, ClassType
from utils import utils
from scheduler.models import ScheduleClassTimeTable, ScheduleVirtualclassMember
from tutor.models import TutorInfo
from course import utils as course_utils
from datetime import timedelta
from django.utils import timezone
from student.models import UserStudentInfo, UserParentInfo
from finance.models import AccountBalance
from django.db.models import Sum


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = TutorInfo
        fields = ('id', 'username', 'total_number_of_class', 'real_name', 'identity_name')


class DeletedBigClassScheduleMemberSerializer(serializers.ListSerializer):

    '''删除 schedule_virtualclass_member中的大班课成员'''

    def to_representation(self, data):
        data = data.filter(class_type_id__in=(ClassType.ONE2ONE, ClassType.SMALLCLASS))
        return super(DeletedBigClassScheduleMemberSerializer, self).to_representation(data)


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


class SmallClassInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassInfo
        fields = ('id', 'class_no', 'class_name_zh', 'class_name', 'create_user_name')


class ClassDetailsSerializer(SmallClassInfoSerializer):

    unit_no = serializers.SerializerMethodField()
    lesson_sum = serializers.SerializerMethodField()

    def get_lesson_sum(self, obj):
        count = ScheduleClassTimeTable.objects.filter(class_field=obj, status__in=(ScheduleClassTimeTable.PUBLISHED, ScheduleClassTimeTable.SUCCESS_APPOINTMENT)).count()
        return count

    def get_unit_no(self, obj):
        return obj.lesson.unit_no

    class Meta(SmallClassInfoSerializer.Meta):
        fields = SmallClassInfoSerializer.Meta.fields + ('lesson_sum', 'class_category', 'class_type_id', 'course_edition_id', 'course_level', 'lesson_no', 'unit_no', 'student_area', 'user_max')


class ClassTimeTableSerializer(serializers.ModelSerializer):

    # week = serializers.SerializerMethodField()
    # tutor_user = TeacherSerializer()
    # class_field = SmallClassInfoSerializer()
    start_time = serializers.SerializerMethodField()
    lesson_info = serializers.SerializerMethodField()
    tutor_user = serializers.SerializerMethodField()

    def get_tutor_user(self, obj):
        if obj.virtual_class:
            return {
                'tutor_username': obj.virtual_class.tutor_user.username,
                'tutor_real_name': obj.virtual_class.tutor_user.real_name,
                'tutor_identity_name': obj.virtual_class.tutor_user.identity_name,
                'tutor_user_id': obj.virtual_class.tutor_user_id
            }

    def get_lesson_info(self, obj):
        vc = VirtualclassInfo.objects.filter(id=obj.virtual_class_id).first()
        if vc:
            return {'lesson_no': vc.lesson.lesson_no,
                    'unit_no': vc.lesson.unit_no,
                    'unit_lesson_no': vc.lesson.unit_lesson_no}

    def get_lesson_no(self, obj):
        vc = VirtualclassInfo.objects.filter(id=obj.virtual_class_id).first()
        if vc:
            return vc.lesson_no
        else:
            lesson = self.get_lesson(obj)
            return {'lesson_no': lesson.lesson_no,
                    'unit_no': lesson.unit_no,
                    'unit_lesson_no': lesson.unit_lesson_no}

    def get_lesson(self, obj):
        now_time = timezone.now()
        count = ScheduleClassTimeTable.objects.filter(class_field=obj.class_field,
                                                      start_time__lt=obj.start_time,
                                                      start_time__gt=now_time,
                                                      status__in=(ScheduleClassTimeTable.PUBLISHED, ScheduleClassTimeTable.SUCCESS_APPOINTMENT)).count()
        lesson = obj.class_field.lesson
        for i in range(1, count+1):
            lesson = course_utils.get_next_lesson(lesson)
        return lesson

    def get_start_time(self, obj):
        return utils.datetime_to_str(obj.start_time)

    # def get_week(self, obj):
    #     return obj.start_time.strftime("%w")

    class Meta:
        model = ScheduleClassTimeTable
        fields = ('id', 'start_time', 'tutor_user', 'lesson_info')


class ScheduleVirtualclassMemberSerializer(BaseScheduleVirtualclassMemberSerializer):

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        start_time = obj.start_time
        end_time = obj.end_time
        if not obj.enter_time:
            return 1   # 缺席
        elif start_time < obj.enter_time + timedelta(minutes=-10):
            return 2  # 迟到
        elif not obj.leave_time or end_time > obj.leave_time:
            return 3  # 早退

    class Meta(BaseScheduleVirtualclassMemberSerializer.Meta):

        fields = BaseScheduleVirtualclassMemberSerializer.Meta.fields + ('status', )


class SmallClassVirtualclassSerializer(serializers.ModelSerializer):

    tutor_user = TeacherSerializer()
    virtual_class_member = ScheduleVirtualclassMemberSerializer(many=True)
    start_time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_start_time(self, obj):
        return utils.datetime_to_str(obj.start_time)

    class Meta:
        model = VirtualclassInfo
        fields = ('id', 'start_time', 'virtual_class_member', 'tutor_user', 'lesson_no')


class ClassMemberParentSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    def get_parent_name(self, obj):
        return obj.username

    class Meta:
        model = UserParentInfo
        fields = ('id', 'parent_name', 'country_of_residence', 'adviser_user_id', 'xg_user_id')


class ClassMemberStudentSerializer(serializers.ModelSerializer):

    parent_user = ClassMemberParentSerializer()
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


class ClassMemberSerializer(serializers.ModelSerializer):
    student_user = ClassMemberStudentSerializer()
    date_join_time = serializers.SerializerMethodField()

    def get_date_join_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    class Meta:
        # list_serializer_class = DeletedBigClassMemberSerializer
        model = ClassMember
        fields = ('id', 'student_user', 'date_join_time')
