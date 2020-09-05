from classroom.models import VirtualclassUnitReport, VirtualclassFirstReport, VirtualclassFirstReportAudit,\
    VirtualclassUnitReportAudit
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from utils.pagination import LargeResultsSetPagination
from utils.viewset_base import JsonResponse
from users.permissions import IsAuthenticated
from unit_report.serializers import UnitReportSerializer, UnitReportDetailSerializer, \
    FirstReportSerializer, FirstReportDetailSerializer
from unit_report.filters import UnitReportFilter, FirstReportFilter, ReportBackend
from rest_framework.decorators import action
from classroom.models import CourseReportFine
from finance.models import BalanceChange
from common.models import ExchangeRate
from django.utils import timezone
from django.conf import settings
from utils.utils import fetch_put_api
from manage.models import UserInfo


class UnitReportViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, ReportBackend)
    filter_class = UnitReportFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('create_time',)

    def get_serializer_class(self):

        if self.action == 'details':
            return UnitReportDetailSerializer
        return UnitReportSerializer

    def struct_user_info(self):
        users = UserInfo.objects.all().only('id', 'username', 'realname')
        result = {}
        for user in users:
            result[user.id] = user
        return result

    def get_serializer_context(self):
        if self.action == 'list':
            return {
                'request': self.request,
                'format': self.format_kwarg,
                'user_infos': self.struct_user_info()
            }
        return {
            'request': self.request,
            'format': self.format_kwarg
        }

    def get_queryset(self):
        queryset = VirtualclassUnitReport.objects.all()
        queryset = queryset.select_related('tutor_user').select_related('virtual_class').select_related('virtual_class__lesson').select_related('virtual_class__lesson__course').select_related('virtual_class__lesson__course__course_edition').select_related('student_user').select_related('student_user__parent_user')
        queryset = queryset.only('id', 'unit_no', 'submit_count', 'first_start_time', 'last_start_time', 'create_time', 'status', 'read_status', 'remark', 'remark_user_id',
                                 'tutor_user__username', 'tutor_user__phone', 'tutor_user__real_name', 'tutor_user__identity_name',
                                 'student_user__id', 'student_user__real_name',
                                 'student_user__parent_user__username', 'student_user__parent_user__xg_user_id', 'student_user__parent_user__adviser_user_id', 'student_user__parent_user__country_of_residence',
                                 'virtual_class__id', 'virtual_class__lesson_no', 'virtual_class__lesson__course__course_edition_id', 'virtual_class__lesson__course__course_level')

        return queryset

    @action(methods=['get'], detail=True)
    def details(self, request, pk):
        unit_report = VirtualclassUnitReport.objects.filter(id=pk).first()

        serializer = self.get_serializer(unit_report)

        return JsonResponse(code=0, msg='success', data=serializer.data, status=status.HTTP_200_OK)

    # 单元报告审核
    @action(methods=['put'], detail=True)
    def examine(self, request, pk):

        statu = request.data.get('status')
        remark = request.data.get('remark')
        report_result_id = request.data.get('report_result_id')
        unit_report = VirtualclassUnitReport.objects.filter(id=pk).first()

        user = request.session.get('user')

        unit_report_audit_url = 'http://' + settings.JAVA_DOMAIN + settings.UNIT_REPORT_AUDIT_URL

        params = {
            'auditUserId': user.get('id'),
            'auditUserName': user.get('realname'),
            # 'createTime': timezone.now(),
            # 'updateTime': timezone.now(),
            'remark': remark,
            'status': statu,
            'unitReportId': unit_report.id
        }
        if report_result_id:
            params['id'] = report_result_id

        result = fetch_put_api(unit_report_audit_url, params, user_id=user.get('id'))
        if not result:
            return JsonResponse(code=1, msg='服务器错误', status=status.HTTP_200_OK)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg=result.get('message'), status=status.HTTP_200_OK)

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 罚金
    @action(methods=['put'], detail=True)
    def impose_fine(self, request, pk):

        money = request.data.get('money')
        remark =request.data.get('remark')

        unit_report = self.get_object()
        # unit_report_fine = CourseReportFine.objects.filter(report_id=pk, type=CourseReportFine.UNIT_REPORT).first()
        # if unit_report_fine:
        #     return JsonResponse(code=1, msg='已经添加罚金', status=status.HTTP_200_OK)

        user = request.session.get('user')

        unit_report_fine = CourseReportFine()
        unit_report_fine.user_id = user.get('id')
        unit_report_fine.report_id = unit_report.id
        unit_report_fine.type = CourseReportFine.UNIT_REPORT
        unit_report_fine.money = money
        unit_report_fine.remark = remark
        unit_report_fine.save()

        now_time = timezone.now()

        rate = ExchangeRate.objects.filter(currency='CNY', valid_start__lte=now_time, valid_end__gt=now_time).first()

        balance_change = BalanceChange()
        balance_change.role = BalanceChange.TEACHER
        balance_change.user_id = unit_report.tutor_user.id
        balance_change.reference = unit_report.virtual_class.id
        balance_change.amount = 0 - (money/rate.rate)
        balance_change.reason = BalanceChange.NO_SHOW_PENALTY
        balance_change.xg_user_id = user.get('id')
        balance_change.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 备注
    @action(methods=['put'], detail=True)
    def remark(self, request, pk):

        unit_report = VirtualclassUnitReport.objects.filter(id=pk).first()

        remark = request.data.get('remark')

        unit_report.remark = remark

        user = request.session.get('user')

        unit_report.remark_user_id = user.get('id')

        unit_report.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)


class FirstReportViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = FirstReportSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, ReportBackend)
    filter_class = FirstReportFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('create_time',)

    def get_serializer_context(self):
        result = {}

        if self.action == 'list':
            users = UserInfo.objects.all().only('id', 'username', 'realname')
            for user in users:
                result[user.id] = user
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'user_infos': result
        }

    def get_queryset(self):

        queryset = VirtualclassFirstReport.objects.all()
        queryset = queryset.select_related('tutor_user').select_related('virtual_class').select_related('virtual_class__lesson').select_related('virtual_class__lesson__course').select_related('student_user').select_related('student_user__parent_user')

        queryset = queryset.only('id', 'start_time', 'tutor_user', 'student_user', 'status', 'submit_count', 'create_time', 'read_status',
                                 'virtual_class__lesson_no', 'virtual_class__lesson__course__course_edition_id', 'virtual_class__lesson__course__course_level',
                                 'tutor_user__username', 'tutor_user__phone', 'tutor_user__real_name', 'tutor_user__identity_name',
                                 'student_user__id', 'student_user__birthday', 'student_user__real_name', 'student_user__gender',
                                 'student_user__parent_user__username', 'student_user__parent_user__xg_user_id', 'student_user__parent_user__adviser_user_id', 'student_user__parent_user__country_of_residence')

        return queryset

    @action(methods=['put'], detail=True)
    def examine(self, request, pk):

        statu = request.data.get('status')
        remark = request.data.get('remark')
        report_result_id = request.data.get('report_result_id')
        first_report = VirtualclassFirstReport.objects.filter(id=pk).first()

        user = request.session.get('user')

        first_report_audit_url = 'http://' + settings.JAVA_DOMAIN + settings.FIRST_REPORT_AUDIT_URL

        params = {
            'auditUserId': user.get('id'),
            'auditUserName': user.get('realname'),
            # 'createTime': timezone.now(),
            # 'updateTime': timezone.now(),
            'remark': remark,
            'status': statu,
            'firstReportId': first_report.id
        }
        if report_result_id:
            params['id'] = report_result_id

        result = fetch_put_api(first_report_audit_url, params, user_id=user.get('id'))

        if not result:
            return JsonResponse(code=1, msg='服务器错误', status=status.HTTP_200_OK)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg=result.get('message'), status=status.HTTP_200_OK)

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def details(self, request, pk):
        first_report = VirtualclassFirstReport.objects.filter(id=pk).first()

        serializer = FirstReportDetailSerializer(first_report)

        return JsonResponse(code=0, msg='success', data=serializer.data, status=status.HTTP_200_OK)

    # 罚金
    @action(methods=['put'], detail=True)
    def impose_fine(self, request, pk):

        money = request.data.get('money')
        remark = request.data.get('remark')

        first_report = self.get_object()
        user = request.session.get('user')

        first_report_fine = CourseReportFine()
        first_report_fine.user_id = user.get('id')
        first_report_fine.report_id = first_report.id
        first_report_fine.type = CourseReportFine.FIRST_REPORT
        first_report_fine.money = money
        first_report_fine.remark = remark
        first_report_fine.save()

        now_time = timezone.now()

        rate = ExchangeRate.objects.filter(currency='CNY', valid_start__lte=now_time, valid_end__gt=now_time).first()

        balance_change = BalanceChange()
        balance_change.role = BalanceChange.TEACHER
        balance_change.user_id = first_report.tutor_user.id
        balance_change.reference = first_report.virtual_class.id
        balance_change.amount = 0 - (money/rate.rate)
        balance_change.reason = BalanceChange.NO_SHOW_PENALTY
        balance_change.adviser_user_id = user.get('id')
        balance_change.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

