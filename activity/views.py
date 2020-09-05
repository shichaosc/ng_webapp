from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.shortcuts import render
from rest_framework import viewsets, status
from utils.viewset_base import JsonResponse
from rest_framework.decorators import action
from finance.models import BalanceChange
from activity.models import ActivityGroupInfo, ActivityGroupRecharge
from activity.serializers import GroupInfoListSerializer, GroupRechargeListSerializer
from activity.filters import GroupActivityFilter, GroupRechargeFilter
from django.conf import settings
from utils.pagination import LargeResultsSetPagination
from django.db import connections
from rest_framework import filters
from users.permissions import IsAuthenticated
import logging

logger = logging.getLogger('pplingo.ng_webapp.classroom')


@permission_required('accounts.can_query_topup_records')
def rechargerecordsquery(request):
    username = request.GET.get('username', None)
    abcs = BalanceChange.objects.filter(user__username=username, reason=BalanceChange.TOP_UP)
    return render(request, 'activity/rechargerecordsquery.html', {'abcs': abcs})


@csrf_exempt
def setfreedelivery(request):
    pass


class GroupActivityViewSet(viewsets.ModelViewSet):

    serializer_class = GroupInfoListSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = GroupActivityFilter
    filter_backends = (filters.OrderingFilter, )
    pagination_class = LargeResultsSetPagination
    queryset = ActivityGroupInfo.objects.all().prefetch_related('group_member').prefetch_related('group_member__parent_user')
    ordering_fields = ('create_time', 'success_time')

    # 创建团购
    @action(methods=['post'], detail=False)
    def create_group_activity(self, request):

        now_date = timezone.now().strftime('%Y%m%d')

        count = ActivityGroupInfo.objects.filter(group_no__contains=now_date).count()

        group_info = ActivityGroupInfo()

        cms_user = request.session.get('user')

        group_info.group_no = int(now_date)*1000 + count

        group_info.user_id = cms_user.get('id')

        group_info.username = cms_user.get('realname')

        group_info.save()
        group_url = 'https://' + settings.STUDENT_USER_DOMAIN + '/activity/group/land-page.html?groupId={}'.format(group_info.id)

        group_info.group_url = group_url

        group_info.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 发放奖励
    @action(methods=['put'], detail=True)
    def give_out_bonus(self, request, pk):

        group_info = ActivityGroupInfo.objects.get(id=pk)

        if group_info.grant_award == ActivityGroupInfo.GRANT:
            return JsonResponse(code=1, msg='已发放奖励', status=status.HTTP_200_OK)

        group_recharges = ActivityGroupRecharge.objects.filter(group_id=group_info.id).all()

        if len(group_recharges) == 0:
            return JsonResponse(code=1, msg='没有成员，不能发放奖励', status=status.HTTP_200_OK)

        for group_recharge in group_recharges:
            order_no = group_recharge.order_no
            recharge_balance_change = BalanceChange.objects.filter(reference=order_no, parent_user_id=group_recharge.parent_user_id, reason=3).first()
            if not recharge_balance_change:
                logger.debug('not found recharge record where order_no={}, parent_user_id={}'.format(order_no, group_recharge.parent_user_id))
            parent_user = group_recharge.parent_user
            balance_change = BalanceChange()
            balance_change.reason = BalanceChange.BONUS
            balance_change.adviser_user_id = parent_user.adviser_user_id
            balance_change.xg_user_id = parent_user.xg_user_id
            balance_change.amount = group_recharge.bonus_amount
            balance_change.normal_amount = 0
            balance_change.reference = group_recharge.order_no
            balance_change.parent_user_id = group_recharge.parent_user_id
            balance_change.user_id = parent_user.id
            balance_change.role = BalanceChange.PARENT
            balance_change.balance_id = recharge_balance_change.balance_id
            balance_change.save()
            # recharge_order = RechargeOrder.objects.filter(order_no=group_recharge.order_no).first()
            # recharge_order.incentive_amount = group_recharge.bonus_amount
            # recharge_order.save()
        group_info.grant_award = ActivityGroupInfo.GRANT
        group_info.save()
        cms_user = request.session.get('user')
        logger.debug('give out bonus, user_id:{}, group_info_id:{}'.format(cms_user.get('id'), group_info.id))
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 总数据
    @action(methods=['get'], detail=False)
    def total_data(self, request):
        '''拼团成功：6团 拼团中：12团 奖励已发放：3团  总充值课时：200课时 总充值人数：60人'''
        '''1：启用；2：拼团成功；3：奖励已发放'''
        sql = '''
            select IFNULL(sum(recharge_amount), 0) as recharge_amount_sum, IFNULL(count(parent_user_id), 0) as parent_user_count, agi.status, count(distinct agi.id) as status_count 
                from activity_group_info agi left join activity_group_recharge agr on agi.id=agr.group_id
                group by agi.status           
        '''
        result = {
            'recharge_sum': 0,
            'parent_user_count': 0,
            '1': 0,
            '2': 0,
            '3': 0
        }
        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                result['recharge_sum'] = result['recharge_sum'] + row[0]
                result['parent_user_count'] = result['parent_user_count'] + row[1]
                result[row[2]] = row[3]

        grant_count = ActivityGroupInfo.objects.filter(grant_award=ActivityGroupInfo.GRANT).count()

        result['3'] = grant_count

        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)


class GroupRechargeViewSet(viewsets.ModelViewSet):

    serializer_class = GroupRechargeListSerializer
    queryset = ActivityGroupRecharge.objects.all().select_related('parent_user')
    filter_class = GroupRechargeFilter




