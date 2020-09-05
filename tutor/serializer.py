from classroom.models import VirtualclassInfo
from common.models import ExchangeRate
from finance.models import BalanceChange
from rest_framework import serializers
import datetime
from tutor.models import TutorInfo
from django.utils import timezone
from scheduler.models import ScheduleTutorClasstype, ScheduleTutorCourse, ScheduleVirtualclassMember
from utils import utils
from datetime import timedelta
from finance.models import RechargeOrder


class ScheduleTutorCourseSerializer(serializers.ModelSerializer):

    course_edition_name = serializers.SerializerMethodField()
    course_level = serializers.SerializerMethodField()

    def get_course_level(self, obj):
        if obj.course:
            return obj.course.course_level

    def get_course_edition_name(self, obj):
        if obj.course:
            return obj.course.course_edition.edition_name

    class Meta:
        model = ScheduleTutorCourse
        fields = ('course_edition_name', 'course_level')


class BaseTutorSerializer(serializers.ModelSerializer):

    teach_age = serializers.SerializerMethodField()  # 教龄
    status = serializers.SerializerMethodField()  # 教师状态  0 上岗不隐藏 1上岗隐藏 2 下岗 3 未激活
    age = serializers.SerializerMethodField()  # 年龄
    tutor_course = ScheduleTutorCourseSerializer(many=True)  # 可教课程

    def get_age(self, obj):
        if obj.birthday:
            return timezone.now().year - obj.birthday.year

    def get_teach_age(self, obj):

        start_of_teaching = obj.teaching_start_time
        if start_of_teaching:
            teach_age = timezone.now() - start_of_teaching
            return float('%.1f' % (teach_age.days/365))
        return None

    def get_status(self, obj):
        if obj.status == TutorInfo.ACTIVE:
            if obj.working == TutorInfo.WORKING:
                if obj.hide == TutorInfo.HIDDEN:  # 隐藏
                    return 1  # 上岗隐藏
                else:
                    return 0  # 上岗不隐藏
            else:
                return 2  # 下岗
        else:
            return 3  # 未激活

    def get_student_sum(self, obj):
        return obj.student_sum

    def get_student_num(self, obj):
        return obj.student_num

    class Meta:
        model = TutorInfo
        fields = ('id', 'username', 'real_name', 'age', 'local_area', 'teach_age', 'tutor_course',
                  'phone', 'status', 'total_number_of_class', 'identity_name')


class TeacherListSerializer(BaseTutorSerializer):

    gender = serializers.SerializerMethodField()
    class_type = serializers.SerializerMethodField()  # 可教班型
    student_num = serializers.SerializerMethodField()  # 现有学生
    student_sum = serializers.SerializerMethodField()  # 累计学生
    working_time = serializers.SerializerMethodField()  # 上岗时间
    first_course_sum = serializers.SerializerMethodField()  # 试听学生
    first_course_recharge_sum = serializers.SerializerMethodField()  # 试听后充值学生

    def get_first_course_recharge_sum(self, obj):
        first_course_recharge_sum = 0
        student_list = ScheduleVirtualclassMember.objects.filter(first_course=ScheduleVirtualclassMember.YES,
                                                  virtual_class__tutor_user=obj,
                                                  virtual_class__status=VirtualclassInfo.FINISH_NOMAL).values(
            'student_user_id', 'virtual_class__start_time', 'student_user__parent_user_id').distinct()

        student_id_list = []
        for student in student_list:
            if student.get('student_user_id') in student_id_list:
                continue
            student_id_list.append(student.get('student_user_id'))
            recharge_order = RechargeOrder.objects.filter(parent_user_id=student.get('student_user__parent_user_id'), update_time__gte=student.get('virtual_class__start_time')).first()
            if recharge_order:
                first_course_recharge_sum = first_course_recharge_sum + 1
        return first_course_recharge_sum

    def get_first_course_sum(self, obj):
        return obj.first_course_sum

    def get_working_time(self, obj):
        if obj.working_time:
            return utils.datetime_to_str(obj.working_time)

    def get_student_sum(self, obj):
        return obj.student_sum

    def get_student_num(self, obj):
        return obj.student_num

    def get_class_type(self, obj):

        class_types = obj.tutor_class_type.all()
        result = []
        for class_type in class_types:
            result.append(class_type.id)
        return result

    def get_gender(self, obj):
        return obj.get_gender_display()

    class Meta(BaseTutorSerializer.Meta):
        fields = BaseTutorSerializer.Meta.fields + ('rating', 'country_of_residence',
                 'gender', 'class_type', 'student_sum',
                 'student_num', 'working_time', 'first_course_sum', 'first_course_recharge_sum')


class StudentAbleTutorSerializer(BaseTutorSerializer):

    student_num = serializers.SerializerMethodField()  # 现有学生
    student_sum = serializers.SerializerMethodField()  # 累计学生

    def get_student_sum(self, obj):
        return obj.student_sum

    def get_student_num(self, obj):
        return obj.student_num

    class Meta(BaseTutorSerializer.Meta):
        fields = BaseTutorSerializer.Meta.fields + ('student_num', 'student_sum')


class TutorVirtualclassSerializer(serializers.ModelSerializer):

    studentname = serializers.SerializerMethodField()
    programme_name = serializers.SerializerMethodField()
    course_level = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    scheduled_time = serializers.SerializerMethodField()
    course_session = serializers.SerializerMethodField()

    def get_scheduled_time(self, obj):
        start_time = obj.start_time + datetime.timedelta(hours=8)
        return datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')

    def get_studentname(self, obj):
        return obj.students
        # print(obj.id)
        # return [student.real_name for student in obj.students]

    def get_salary(self, obj):
        # 获得工资基数
        result = {
            'base_salary': 0,
            'incentive_salary': 0,
            'student_absence_salary': 0,
            'tutor_absence_salary': 0,
            'currency': ExchangeRate.default_currency
        }
        now_time = timezone.now()
        rate = ExchangeRate.objects.filter(currency=ExchangeRate.default_currency, valid_start__lte=now_time, valid_end__gt=now_time)
        exchange_rate = rate.first().rate

        singapore_rate = ExchangeRate.objects.filter(currency='SGD', valid_start__lte=now_time, valid_end__gt=now_time)
        singapore_exchange_rate = singapore_rate.first().rate

        teacher = obj.tutor_user

        if teacher.local_area == TutorInfo.SINGAPORE:
            exchange_rate = singapore_exchange_rate
            result['currency'] = 'SGD'

        accounts = BalanceChange.objects.filter(
            reason__in=[BalanceChange.DELIVERY, BalanceChange.INCENTIVE, BalanceChange.ABSENCE_COMPENSATION, BalanceChange.NO_SHOW_PENALTY],
            reference=obj.id,
            user_id=teacher.id,
            role=BalanceChange.TEACHER).all()

        for account in accounts:
            if account.reason == BalanceChange.DELIVERY:  # 基本工资
                result['base_salary'] = float(account.amount * exchange_rate)
            if account.reason == BalanceChange.INCENTIVE:  # 奖励
                result['incentive_salary'] = float(account.amount * exchange_rate)
            if account.reason == BalanceChange.ABSENCE_COMPENSATION:  # 学生缺席奖励
                result['student_absence_salary'] = result['student_absence_salary'] + float(account.amount * exchange_rate)
            if account.reason == BalanceChange.NO_SHOW_PENALTY:  # 老师缺席惩罚
                result['tutor_absence_salary'] = result['tutor_absence_salary'] + float(account.amount * exchange_rate)

        return result

    def get_programme_name(self, obj):
        if obj.lesson:
            return obj.lesson.course.course_edition.edition_name
        return None

    def get_course_level(self, obj):
        if obj.lesson:
            return obj.lesson.course.course_level
        return None

    def get_course_session(self, obj):
        if obj.lesson:
            return obj.lesson.lesson_no
        return None

    class Meta:
        model = VirtualclassInfo
        fields = ('id', 'studentname', 'scheduled_time', 'programme_name', 'course_level', 'course_session', 'salary')


class MatchTutorInfoSerializer(serializers.ModelSerializer):

    student_count = serializers.SerializerMethodField()  # 当前学生数量
    status = serializers.SerializerMethodField()  # 老师状态
    teach_age = serializers.SerializerMethodField()  # 教龄

    def get_teach_age(self, obj):

        start_of_teaching = obj.teaching_start_time
        if start_of_teaching:
            teach_age = timezone.now() - start_of_teaching
            return float('%.1f' % (teach_age.days/365))
        return None

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

    def get_student_count(self, obj):
        return obj.student_count

    class Meta:
        model = TutorInfo
        fields = ('id', 'username', 'real_name', 'identity_name', 'phone', 'local_area',
                  'student_count', 'status', 'total_number_of_class', 'teach_age')
