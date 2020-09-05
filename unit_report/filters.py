from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from classroom.models import VirtualclassUnitReport, VirtualclassFirstReport, ClassType
from django.db.models import Q
from manage.models import UserInfo
from rest_framework import filters
from utils import utils
import datetime


class ReportBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        search_day = request.query_params.get('search_day', None)
        if search_day:  # 过滤今天明天后天。。。
            search_day = int(search_day)
            if search_day == -7:
                end, _ = utils.get_day_start_end()
                seven_day = utils.get_few_date_time(day=search_day)
                _, start = utils.get_day_start_end(seven_day)
                kwargs['create_time' + '__gte'] = start
                kwargs['create_time' + '__lt'] = end
            else:
                before_day = utils.get_few_date_time(day=search_day)
                start, end = utils.get_day_start_end(before_day)
                kwargs['create_time' + '__gte'] = start
                kwargs['create_time' + '__lt'] = end
        else:   # 过滤时间段
            start_time = request.query_params.get('start_time', None)
            end_time = request.query_params.get('end_time', None)
            if start_time:
                start_time = "{} 00:00:00".format(start_time)
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utils.tz)
                kwargs['create_time' + '__gte'] = start_time
            if end_time:
                end_time = "{} 23:59:59".format(end_time)
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utils.tz)
                kwargs['create_time' + '__lte'] = end_time
        return queryset.filter(**kwargs)


class UnitReportFilter(FilterSet):

    status = NumberFilter(method='status_filter', label='status')
    id = NumberFilter('id')
    student_name = CharFilter(method='student_name_filter', label='student_name')
    course_edition = NumberFilter(method='course_edition_filter', label='course_edition')
    course_level = NumberFilter(method='course_level_filter', label='course_level')
    course_unit = NumberFilter('unit_no')
    user_name = CharFilter(method='user_name_filter', label='user_name')
    tutor_name = CharFilter(method='tutor_name_filter', label='tutor_name')
    send_parent = NumberFilter('status')
    examine_user = CharFilter(method='examine_user_filter', label='examine_user')

    def examine_user_filter(self, queryset, name, value):
        cms_user = UserInfo.objects.filter(realname__icontains=value).first()
        if not cms_user:
            return queryset
        queryset = queryset.filter(unit_report_audit__audit_user_id=cms_user.id)
        return queryset


    def status_filter(self, queryset, name, value):
        if int(value) == VirtualclassUnitReport.EXAMINED:
            queryset = queryset.filter(Q(status=VirtualclassUnitReport.EXAMINED)|Q(status=VirtualclassUnitReport.SAVED))
        else:
            queryset = queryset.filter(status=value)
        return queryset

    def tutor_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(tutor_user__username__icontains=value) | Q(tutor_user__email__icontains=value) | Q(tutor_user__phone__icontains=value) | Q(
                tutor_user__real_name__icontains=value))
        return queryset

    def user_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(student_user__parent_user__adviser_user_id=value) | Q(student_user__parent_user__xg_user_id=value))
        return queryset

    def student_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(student_user__real_name__icontains=value) |
            Q(student_user__parent_user__username__icontains=value) |
            Q(student_user__parent_user__email__icontains=value) |
            Q(student_user__parent_user__phone__icontains=value))
        return queryset

    def course_edition_filter(self, queryset, name, value):
        queryset = queryset.filter(virtual_class__lesson__course__course_edition_id=value)
        return queryset

    def course_level_filter(self, queryset, name, value):
        queryset = queryset.filter(virtual_class__lesson__course__course_level=value)
        return queryset

    class Meta:
        model = VirtualclassUnitReport
        fields = ['id', 'status', 'student_name', 'course_edition', 'course_level',
                  'course_unit', 'user_name', 'tutor_name', 'send_parent', 'examine_user']


class FirstReportFilter(FilterSet):

    status = NumberFilter(method='status_filter', label='status')
    id = NumberFilter('id')
    student_name = CharFilter(method='student_name_filter', label='student_name')
    course_edition = NumberFilter(method='course_edition_filter', label='course_edition')
    course_level = NumberFilter(method='course_level_filter', label='course_level')
    course_unit = NumberFilter('unit_no')
    user_name = CharFilter(method='user_name_filter', label='user_name')
    tutor_name = CharFilter(method='tutor_name_filter', label='tutor_name')
    send_parent = NumberFilter('status')
    examine_user = CharFilter(method='examine_user_filter', label='examine_user')

    def examine_user_filter(self, queryset, name, value):
        cms_user = UserInfo.objects.filter(realname__icontains=value).first()
        if not cms_user:
            return queryset
        queryset = queryset.filter(first_report_audit__audit_user_id=cms_user.id)
        return queryset

    def status_filter(self, queryset, name, value):
        if int(value) == VirtualclassUnitReport.EXAMINED:
            queryset = queryset.filter(Q(status=VirtualclassUnitReport.EXAMINED)|Q(status=VirtualclassUnitReport.SAVED))
        else:
            queryset = queryset.filter(status=value)
        return queryset

    def tutor_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(tutor_user__username__icontains=value) | Q(tutor_user__email__icontains=value) | Q(tutor_user__phone__icontains=value) | Q(
                tutor_user__real_name__icontains=value))
        return queryset

    def user_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(student_user__parent_user__adviser_user_id=value) | Q(student_user__parent_user__xg_user_id=value))
        return queryset

    def student_name_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(student_user__real_name__icontains=value) |
            Q(student_user__parent_user__username__icontains=value) |
            Q(student_user__parent_user__email__icontains=value) |
            Q(student_user__parent_user__phone__icontains=value))
        return queryset

    def course_edition_filter(self, queryset, name, value):
        queryset = queryset.filter(virtual_class__lesson__course__course_edition_id=value)
        return queryset

    def course_level_filter(self, queryset, name, value):
        queryset = queryset.filter(virtual_class__lesson__course__course_level=value)
        return queryset

    class Meta:
        model = VirtualclassFirstReport
        fields = ['id', 'status', 'student_name', 'course_edition', 'course_level',
                  'course_unit', 'user_name', 'tutor_name', 'send_parent', 'examine_user']
