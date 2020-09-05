from rest_framework import serializers
from classroom.models import VirtualclassInfo
from utils import utils
from finance.models import BalanceChange, RechargeOrder, BuyPackage
from common.models import CommonBussinessRule, CommonRuleFormula
from student.models import UserStudentInfo
from student.serializers import RechargeParentUser
from manage.models import UserInfo


class RechargeSerializer(serializers.ModelSerializer):

    parent_user = RechargeParentUser()  # 学生信息
    update_time = serializers.SerializerMethodField()  # 充值时间
    recharge_count = serializers.SerializerMethodField()  # 充值次数
    activity = serializers.SerializerMethodField()   # 活动
    recharge_type = serializers.SerializerMethodField()   # 交易类型
    redeem_code = serializers.SerializerMethodField()   # 充值卡卡号
    coupon_code = serializers.SerializerMethodField()   # 优惠券号
    course_adviser = serializers.SerializerMethodField()  # 课程顾问
    learn_manager = serializers.SerializerMethodField()   # 学管
    recharge_amount = serializers.SerializerMethodField()  # 充值课时
    incentive_amount = serializers.SerializerMethodField()  # 赠送课时

    def get_recharge_amount(self, obj):
        if obj.recharge_amount:
            return '%.2f' % obj.recharge_amount

    def get_incentive_amount(self, obj):
        if obj.incentive_amount:
            return '%.2f' % obj.incentive_amount

    def get_course_adviser(self, obj):
        if obj.adviser_user_id:
            cms_user = UserInfo.objects.filter(id=obj.adviser_user_id).first()
            if cms_user:
                return cms_user.realname

    def get_learn_manager(self, obj):
        if obj.xg_user_id:
            cms_user = UserInfo.objects.filter(id=obj.xg_user_id).first()
            if cms_user:
                return cms_user.realname

    def get_recharge_type(self, obj):
        return obj.get_recharge_type_display()

    def get_redeem_code(self, obj):
        if obj.recharge_type == RechargeOrder.RECHARGE_CARD:
            return obj.code

    def get_coupon_code(self, obj):
        if obj.recharge_type != RechargeOrder.RECHARGE_CARD:
            return obj.code

    def get_valid_date(self, obj):
        if obj.recharge_type == RechargeOrder.PACKAGE:
            buy_package = BuyPackage.objects.filter(order_no=obj.order_no)
            if buy_package:
                return utils.datetime_to_str(buy_package.valid_start) + '~' + utils.datetime_to_str(buy_package.valid_end)
        else:
            return '永久有效'

    def get_activity(self, obj):
        if obj.recharge_type == RechargeOrder.RECHARGE_CARD:
            return '充值卡'
        elif obj.recharge_type == RechargeOrder.PACKAGE:
            return '课程包'

        rule_formula = CommonRuleFormula.objects.filter(rule__rule_type=CommonBussinessRule.BASE_PAY,
                                                        rule__valid_start__lt=obj.update_time,
                                                        rule__valid_end__gt=obj.update_time,
                                                        min_amount__lt=obj.recharge_amount,
                                                        max_amount__gt=obj.recharge_amount).first()
        if rule_formula:
            return rule_formula.rule.remark

    def get_recharge_count(self, obj):

        return obj.recharge_count

    def get_update_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    class Meta:
        model = RechargeOrder
        fields = ('recharge_amount', 'incentive_amount', 'parent_user', 'recharge_count', 'activity',
                  'update_time', 'coupon_code', 'recharge_type', 'order_no', 'redeem_code', 'course_adviser',
                  'learn_manager')


class AdHocSerializer(serializers.ModelSerializer):

    student = serializers.SerializerMethodField()
    virtualclass = serializers.SerializerMethodField()
    lesson_sum = serializers.SerializerMethodField()  # 第几次上课
    course_adviser = serializers.SerializerMethodField()  # 课程顾问
    learn_manager = serializers.SerializerMethodField()  # 学管
    transaction_type = serializers.SerializerMethodField()   # 消耗课时类型

    def get_transaction_type(self, obj):
        return '账户余额'

    def get_course_adviser(self, obj):
        course_adviser_id = obj.adviser_user_id
        if course_adviser_id:
            course_adviser = UserInfo.objects.filter(id=course_adviser_id).first()
            if course_adviser:
                return course_adviser.realname

    def get_learn_manager(self, obj):
        learn_manager_id = obj.xg_user_id
        if learn_manager_id:
            learn_manager = UserInfo.objects.filter(id=learn_manager_id).first()
            if learn_manager:
                return learn_manager.realname

    def get_student(self, obj):
        student = UserStudentInfo.objects.filter(id=obj.user_id).first()
        if student:
            return {
                'student_id': str(student.id),
                'student_name': student.real_name
            }

    def get_lesson_sum(self, obj):
        return obj.lesson_sum

    def get_virtualclass(self, obj):
        vc = VirtualclassInfo.objects.filter(id=obj.reference).first()
        if vc:
            scheduled_time = vc.start_time
            class_type = vc.class_type.name
            course_lesson = vc.lesson
            course_info = {
                'edition_name': course_lesson.course.course_edition.edition_name,
                'course_level': course_lesson.course.course_level,
                'lesson_no': course_lesson.lesson_no
            }
            teacher_name = vc.tutor_user.__str__()
            return dict(scheduled_time=utils.datetime_to_str(scheduled_time),
                        class_type=class_type,
                        course_info=course_info,
                        teacher_name=teacher_name,
                        remark=None)

    class Meta:
        model = BalanceChange
        fields = ('amount', 'student', 'virtualclass', 'lesson_sum',
                  'course_adviser', 'learn_manager', 'transaction_type')
