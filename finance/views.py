from rest_framework import viewsets, exceptions, status
from rest_framework.decorators import action
from utils.pagination import LargeResultsSetPagination
from finance.models import BalanceChange, RechargeOrder
from users.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from finance.serializer import RechargeSerializer, AdHocSerializer
from finance.filters import RechargeFilter, BalanceChangeFilter
from utils import utils
from django.db import connections
from utils.viewset_base import JsonResponse


class RechargeViewSet(viewsets.ModelViewSet):

    serializer_class = RechargeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = RechargeFilter
    permissions = (IsAuthenticated, )
    ordering_fields = ('update_time',)

    def permission_denied(self, request, message=None):
        '''
        没有权限时的返回值
        :param request:
        :param message:
        :return:
        '''
        if not message:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message)

    def get_queryset(self):

        recharge_count = """select count(*) from finance_recharge_order fro where fro.create_time <= finance_recharge_order.create_time and fro.parent_user_id = finance_recharge_order.parent_user_id and fro.status=1"""
        adviser_user_id = '''select fbc.adviser_user_id from finance_balance_change fbc where fbc.reference=finance_recharge_order.order_no and fbc.reason=3 limit 1'''
        xg_user_id = '''select fbc.xg_user_id from finance_balance_change fbc where fbc.reference=finance_recharge_order.order_no and fbc.reason=3 limit 1'''
        queryset = RechargeOrder.objects.filter(status=RechargeOrder.PAID).all()
        queryset = queryset.extra(
            select={'recharge_count': recharge_count}
        ).extra(
            select={'xg_user_id': xg_user_id}
        ).extra(
            select={'adviser_user_id': adviser_user_id}
        )

        cms_user_id = self.request.query_params.get('cms_user_id')
        if cms_user_id:
            query_sql = "({})={} or ({})={}".format(adviser_user_id, cms_user_id, xg_user_id, cms_user_id)
            queryset = queryset.extra(where=[query_sql])
        return queryset


class AttendClassInfoViewSet(viewsets.ModelViewSet):

    serializer_class = AdHocSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = BalanceChangeFilter
    permissions = (IsAuthenticated,)
    ordering_fields = ('create_time',)

    def permission_denied(self, request, message=None):
        '''
        没有权限时的返回值
        :param request:
        :param message:
        :return:
        '''
        if not message:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message)

    def get_queryset(self):

        queryset = BalanceChange.objects.filter(reason=BalanceChange.AD_HOC).extra(
            select={
                'lesson_sum': """select count(fbc.id) from finance_balance_change fbc where fbc.create_time <= finance_balance_change.create_time and fbc.user_id = finance_balance_change.user_id and fbc.reason=1"""
            }
        )
        cms_user_id = self.request.query_params.get('cms_user_id')
        if cms_user_id:
            query_sql = "adviser_user_id={} or xg_user_id={}".format(cms_user_id, cms_user_id)
            queryset = queryset.extra(where=[query_sql])
        return queryset


class StatisticsViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )

    def permission_denied(self, request, message=None):
        '''
        没有权限时的返回值
        :param request:
        :param message:
        :return:
        '''
        if not message:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message)

    @action(methods=['get'], detail=False)
    def recharge(self, request):
        month_query = request.query_params.get('month_query')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        cms_user_id = request.query_params.get('cms_user_id')
        month_begin = None
        month_end = None
        if month_query == 'this_month':
            month_begin, month_end = utils.getNowMonth()
        elif month_query == 'before_month':
            month_begin, month_end = utils.get_berfore_month_datetime()

        balance_change_sql = """SELECT
            fbc.amount,
            fbc.adviser_user_id,
            fbc.xg_user_id
        FROM
            finance_balance_change fbc
        WHERE
            fbc.reason in({}, {})
            AND ( fbc.adviser_user_id IS NOT NULL OR fbc.xg_user_id IS NOT NULL )""".format(
            BalanceChange.TOP_UP, BalanceChange.REDEEM)

        if month_begin:
            balance_change_sql = balance_change_sql + " and fbc.create_time>='{}'".format(utils.datetime_str(month_begin))
        if month_end:
            balance_change_sql = balance_change_sql + " and fbc.create_time<='{}'".format(utils.datetime_str(month_end))
        if start_time:
            start_time = "{} 00:00:00".format(start_time)
            balance_change_sql = balance_change_sql + " and fbc.create_time>='{}'".format(start_time)
        if end_time:
            end_time = "{} 23:59:59".format(end_time)
            balance_change_sql = balance_change_sql + " and fbc.create_time<='{}'".format(end_time)
        if cms_user_id:
            balance_change_sql = balance_change_sql + " and (fbc.xg_user_id={} or fbc.adviser_user_id={})".format(cms_user_id, cms_user_id)

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(balance_change_sql)
            rows = cursor.fetchall()
        new_student_amount = 0
        old_student_amount = 0
        for row in rows:
            if row[2]:
                old_student_amount = old_student_amount + row[0]
            elif row[1]:
                new_student_amount = new_student_amount + row[0]
        data = dict(new_student_amount=new_student_amount, old_student_amount=old_student_amount)
        return JsonResponse(code=0, msg='success', data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def ad_hoc(self, request):
        month_query = request.query_params.get('month_query')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        cms_user_id = request.query_params.get('cms_user_id')

        month_begin = None
        month_end = None
        if month_query == 'this_month':
            month_begin, month_end = utils.getNowMonth()
        elif month_query == 'before_month':
            month_begin, month_end = utils.get_berfore_month_datetime()

        balance_change_sql = """SELECT
            fbc.amount,
            fbc.adviser_user_id,
            fbc.xg_user_id
        FROM
            finance_balance_change fbc
        WHERE
            fbc.reason={}
            AND ( fbc.adviser_user_id IS NOT NULL OR fbc.xg_user_id IS NOT NULL )""".format(BalanceChange.AD_HOC)

        if month_begin:
            balance_change_sql = balance_change_sql + " and fbc.create_time>='{}'".format(
                utils.datetime_str(month_begin))
        if month_end:
            balance_change_sql = balance_change_sql + " and fbc.create_time<='{}'".format(
                utils.datetime_str(month_end))
        if start_time:
            start_time = "{} 00:00:00".format(start_time)

            balance_change_sql = balance_change_sql + " and fbc.create_time>='{}'".format(start_time)
        if end_time:
            end_time = "{} 23:59:59".format(end_time)
            balance_change_sql = balance_change_sql + " and fbc.create_time<='{}'".format(end_time)
        if cms_user_id:
            balance_change_sql = balance_change_sql + " and (fbc.xg_user_id={} or fbc.adviser_user_id={})".format(cms_user_id, cms_user_id)
        with connections['lingoace'].cursor() as cursor:
            cursor.execute(balance_change_sql)
            rows = cursor.fetchall()
        new_student_amount = 0
        old_student_amount = 0
        for row in rows:
            if row[2]:
                old_student_amount = old_student_amount + row[0]
            elif row[1]:
                new_student_amount = new_student_amount + row[0]
        data = dict(new_student_amount=new_student_amount, old_student_amount=old_student_amount)
        return JsonResponse(code=0, msg='success', data=data, status=status.HTTP_200_OK)


