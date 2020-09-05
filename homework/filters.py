from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, OrderingFilter
import datetime
from utils import utils
from finance.models import RechargeOrder, BalanceChange
import pytz
from django.db.models import Q
from homework.models import HomeworkQuestionInfo, HomeworkOutlineGroup, \
    HomeworkOutlineInfo, HomeworkKnowledgePoint


class HomeworkOutlineGroupFilter(FilterSet):

    lesson_id = NumberFilter(method='lesson_id_filter', label='lesson_id')
    type = NumberFilter('type')
    outline_id = NumberFilter('outline_id')

    def lesson_id_filter(self, queryset, name, value):

        queryset = queryset.filter(lesson_id=value, outline__status__in=(HomeworkOutlineInfo.NOT_FINISH, HomeworkOutlineInfo.ACTIVE))
        return queryset

    class Meta:
        model = HomeworkOutlineGroup
        fields = ['lesson_id', 'type', 'outline_id']
