from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from django.db.models import Q
from student.config import AMBASSADOR, REFERER, DIRECT
from student.models import UserStudentInfo
from classroom.models import ClassInfo
from rest_framework import filters
from utils import utils
import datetime
from course.models import CourseLesson, CourseEdition, CourseInfo


class StudentFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kwargs = {}
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


class StudentManagerFilter(FilterSet):

    student_name = CharFilter(method='student_name_filter', label='student_name')
    programme_name = NumberFilter('course_edition_id')
    course_level = NumberFilter('course_level')
    cms_user = NumberFilter(method='cms_user_filter', label='cms_user')
    student_source = CharFilter(method='student_source_filter', label='student_source')
    class_id = CharFilter(method='class_id_filter', label='class_id')

    def class_id_filter(self, queryset, name, value):
        class_info = ClassInfo.objects.filter(id=value).only('package_id').first()
        queryset = queryset.filter(subscription__package_price__package_id=class_info.package_id).distinct()
        return queryset

    def student_name_filter(self, queryset, name, value):
        student_list = UserStudentInfo.objects.filter(
            Q(real_name__icontains=value) | Q(parent_user__username__icontains=value) | Q(
                parent_user__email__icontains=value) | Q(parent_user__phone__icontains=value)).only(
            'id').all()[:100]
        student_ids = []
        for student in student_list:
            student_ids.append(student.id)
        if len(student_ids) < 100:
            queryset = queryset.filter(id__in=student_ids)
        else:
            queryset = queryset.filter(
                Q(real_name__icontains=value) |
                Q(parent_user__username__icontains=value) |
                Q(parent_user__email__icontains=value) |
                Q(parent_user__phone__icontains=value))
        return queryset

    def student_source_filter(self, queryset, name, value):
        if value == DIRECT:
            queryset = queryset.filter(parent_user__code__isnull=True, parent_user__referrer_user_id__isnull=True)
        if value == AMBASSADOR:
            queryset = queryset.filter(parent_user__code__isnull=False)
        elif value == REFERER:
            queryset = queryset.filter(parent_user__referrer_user_id__isnull=False)
        return queryset

    def cms_user_filter(self, queryset, name, value):
        if value == -1:
            queryset = queryset.filter(parent_user__adviser_user_id__isnull=True)
        else:
            queryset = queryset.filter(Q(parent_user__adviser_user_id=value)|Q(parent_user__xg_user_id=value))
        return queryset

    class Meta:
        model = UserStudentInfo
        fields = ['student_name', 'programme_name', 'course_level', 'cms_user', 'student_source', 'class_id']


class OldStudentManagerFilter(FilterSet):

    student_name = CharFilter(method='student_name_filter', label='student_name')
    programme_name = CharFilter(method='programme_name_filter', label='programme_name')
    course_level = NumberFilter('course_level')
    cms_user = NumberFilter(method='cms_user_filter', label='cms_user')
    source = CharFilter(method='student_source_filter', label='source')

    def programme_name_filter(self, queryset, name, value):
        queryset = queryset.filter(course_edition_id=value)
        return queryset

    def student_name_filter(self, queryset, name, value):
        student_list = UserStudentInfo.objects.filter(
            Q(real_name__icontains=value) | Q(parent_user__username__icontains=value) | Q(
                parent_user__email__icontains=value) | Q(parent_user__phone__icontains=value)).only(
            'id').all()[:100]
        student_ids = []
        for student in student_list:
            student_ids.append(student.id)
        if len(student_ids) < 100:
            queryset = queryset.filter(id__in=student_ids)
        else:
            queryset = queryset.filter(
                Q(real_name__icontains=value)|
                Q(parent_user__username__icontains=value)|
                Q(parent_user__email__icontains=value)|
                Q(parent_user__phone__icontains=value))
        return queryset

    def student_source_filter(self, queryset, name, value):
        if value == DIRECT:
            queryset = queryset.filter(parent_user__code__isnull=True, parent_user__referrer_user_id__isnull=True)
        if value == AMBASSADOR:
            queryset = queryset.filter(parent_user__code__isnull=False)
        elif value == REFERER:
            queryset = queryset.filter(parent_user__referrer_user_id__isnull=False)
        return queryset

    def cms_user_filter(self, queryset, name, value):
        if value == -1:
            queryset = queryset.filter(Q(parent_user__adviser_user_id__isnull=True) | Q(parent_user__xg_user_id__isnull=True))
        else:
            queryset = queryset.filter(Q(parent_user__adviser_user_id=value)|Q(parent_user__xg_user_id=value))
        return queryset

    class Meta:
        model = UserStudentInfo
        fields = ['student_name', 'programme_name', 'course_level', 'cms_user', 'source']
