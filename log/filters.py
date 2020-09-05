from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from rest_framework import filters
from manager.log.models import ManagerLog


class ManagerLogFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)

        if start_time:
            kwargs['create_time' + '__gte'] = start_time
        if end_time:
            kwargs['create_time' + '__lte'] = end_time

        return queryset.filter(**kwargs)


class ManagerLogFilter(FilterSet):

    realname = CharFilter('user__realname', lookup_expr='icontains')
    type = NumberFilter('type')
    operate_name = CharFilter('operate_name', lookup_expr='icontains')
    operate_name = CharFilter('operate_name', lookup_expr='icontains')


    class Meta:
        model = ManagerLog
        fields = ['realname', ]
