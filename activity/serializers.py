from rest_framework import serializers
from utils import utils
from student.models import UserStudentInfo, UserParentInfo
from activity.models import ActivityGroupInfo, ActivityGroupRecharge
from finance.models import BalanceChange, RechargeOrder
from student.models import UserIp


class GroupParentUserSerializer(serializers.ModelSerializer):

    country_of_residence = serializers.SerializerMethodField()

    def get_country_of_residence(self, obj):
        user_ip = UserIp.objects.filter(username=obj.username, role=UserParentInfo.PARENT).first()
        if user_ip:
            return user_ip.country

    class Meta:
        model = UserParentInfo
        fields = ('id', 'username', 'country_of_residence', 'xg_user_name', 'adviser_user_name')


class GroupRechargeSerializer(serializers.ModelSerializer):

    parent_user = GroupParentUserSerializer()

    class Meta:
        model = ActivityGroupRecharge
        fields = ('id', 'parent_user', 'recharge_amount', 'bonus_amount')


class GroupInfoListSerializer(serializers.ModelSerializer):

    group_member = GroupRechargeSerializer(many=True)
    create_time = serializers.SerializerMethodField()  # 团创建时间
    success_time = serializers.SerializerMethodField()  # 拼团成功时间
    # recharge_amount_sum = serializers.SerializerMethodField()  # 充值课时
    #
    # def get_recharge_amount_sum(self, obj):
    #
    #     recharge_amount_sum = ActivityGroupRecharge.objects.filter(group_id=obj.id).annotate(sum=Sum("recharge_amount"))
    #
    #     return recharge_amount_sum

    def get_success_time(self, obj):
        if obj.success_time:
            return utils.datetime_to_str(obj.success_time)

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    class Meta:
        model = ActivityGroupInfo
        fields = ('id', 'group_member', 'create_time', 'success_time', 'group_no', 'group_url', 'username', 'status', 'grant_award')


class GroupRechargeListSerializer(serializers.ModelSerializer):

    parent_user = GroupParentUserSerializer()
    recharge_order = serializers.SerializerMethodField()  # 课程顾问学管

    def get_recharge_order(self, obj):
        if not obj.order_no:
            return None
        recharge_order = RechargeOrder.objects.filter(order_no=obj.order_no, status=RechargeOrder.PAID).first()
        if not recharge_order:
            return None
        return {
            'recharge_time': utils.datetime_to_str(recharge_order.update_time),
            'currency': recharge_order.currency,
            'recharge_amount': recharge_order.recharge_amount,
            'bonus_amount': recharge_order.incentive_amount
        }

    class Meta:
        model = ActivityGroupRecharge
        fields = ('id', 'parent_user', 'recharge_order', 'order_no', 'recharge_amount')


