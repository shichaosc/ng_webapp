from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, OrderingFilter
import datetime
from utils import utils
from finance.models import RechargeOrder, BalanceChange
import pytz
from django.db.models import Q
from student.models import UserStudentInfo


class RechargeFilter(FilterSet):

    month_query = CharFilter(method='month_query_filter', label='month_query')
    start_time = CharFilter(method='start_time_filter', label='start_time')
    end_time = CharFilter(method='end_time_filter', label='end_time')
    parent_name = CharFilter(method='parent_name_filter', label='parent_name')

    def month_query_filter(self, queryset, name, value):
        if not value:
            return queryset
        if value == 'this_month':
            month_begin, month_end = utils.getNowMonth()
            queryset = queryset.filter(create_time__gte=month_begin, create_time__lte=month_end)
        elif value == 'before_month':
            month_begin, month_end = utils.get_berfore_month_datetime()
            queryset = queryset.filter(create_time__gte=month_begin, create_time__lte=month_end)
        return queryset

    def start_time_filter(self, queryset, name, value):
        if value:
            start_time = "{} 00:00:00".format(value)
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)

            queryset = queryset.filter(create_time__gte=start_time)
        return queryset

    def end_time_filter(self, queryset, name, value):
        if value:
            end_time = "{} 23:59:59".format(value)
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
            queryset = queryset.filter(create_time__lte=end_time)
        return queryset

    def parent_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(parent_user__username=value)|Q(parent_user__phone=value)|Q(parent_user__email=value))
        return queryset

    class Meta:
        model = RechargeOrder
        fields = ['month_query', 'start_time', 'end_time', 'parent_name']


class BalanceChangeFilter(FilterSet):

    month_query = CharFilter(method='month_query_filter', label='month_query')
    start_time = CharFilter(method='start_time_filter', label='start_time')
    end_time = CharFilter(method='end_time_filter', label='end_time')
    student_name = CharFilter(method='student_name_filter', label='student_name')

    def month_query_filter(self, queryset, name, value):
        if not value:
            return queryset
        if value == 'this_month':
            month_begin, month_end = utils.getNowMonth()
            queryset = queryset.filter(create_time__gte=month_begin, create_time__lte=month_end)
        elif value == 'before_month':
            month_begin, month_end = utils.get_berfore_month_datetime()
            queryset = queryset.filter(create_time__gte=month_begin, create_time__lte=month_end)
        return queryset

    def start_time_filter(self, queryset, name, value):
        if value:
            start_time = "{} 00:00:00".format(value)
            queryset = queryset.filter(create_time__gte=start_time)
        return queryset

    def end_time_filter(self, queryset, name, value):
        if value:
            end_time = "{} 23:59:59".format(value)
            queryset = queryset.filter(create_time__lte=end_time)
        return queryset

    def student_name_filter(self, queryset, name, value):
        student_ids = UserStudentInfo.objects.filter(real_name__contains=value).values('id').all()
        queryset = queryset.filter(user_id__in=student_ids)
        return queryset

    class Meta:
        model = BalanceChange
        fields = ['month_query', 'start_time', 'end_time', 'student_name']

