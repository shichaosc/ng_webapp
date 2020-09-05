from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from activity.models import ActivityGroupRecharge, ActivityGroupInfo
from django.db.models import Q


class GroupActivityFilter(FilterSet):

    status = NumberFilter(method='status_filter', label='status')
    create_user_id = NumberFilter('user_id')
    group_no = CharFilter('group_no')
    parent_user = CharFilter(method='parent_user_filter', label='parent_user')
    grant_status = CharFilter(method='grant_status_filter', label='grant_status')

    def grant_status_filter(self, queryset, name, value):
        queryset = queryset.filter(grant_award=value)
        return queryset

    def parent_user_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(group_member__parent_user__username__contains=value)|Q(group_member__parent_user__real_name__contains=value))
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(status=value)
        return queryset

    class Meta:
        model = ActivityGroupInfo
        fields = ['status', 'create_user_id', 'grant_status', 'parent_user']


class GroupRechargeFilter(FilterSet):

    group_id = NumberFilter('group_id')

    class Meta:
        model = ActivityGroupRecharge
        fields = ['group_id']
