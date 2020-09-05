from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from utils import utils
import datetime
from tutor.models import TutorInfo
from django.db.models import Q
from scheduler.models import TutorTimetable
from classroom.models import VirtualclassInfo
from rest_framework import filters
from student.models import UserStudentInfo


class TeacherFilter(FilterSet):

    teacher_name = CharFilter(method='filter_teacher_name', label='filter_teacher_name')
    course_edition = CharFilter(method='course_edition_filter', label='course_edition')
    course_level = CharFilter(method='course_level_filter', label='course_level')
    class_type = CharFilter(method='class_type_filter', label='class_type')
    date_day = CharFilter(method='date_day_filter', label='date_day')
    local_area = NumberFilter('local_area')
    status = CharFilter(method='status_filter', label='status')
    full_work = CharFilter(method='full_work_filter', label='full_work')

    def full_work_filter(self, queryset, name, value):
        queryset = queryset.filter(full_work=value)
        return queryset
    # def start_time_filter(self, queryset, name, value):
    #
    #     UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    #
    #     start_time = datetime.datetime.strptime(value, UTC_FORMAT)
    #     before_time = start_time + datetime.timedelta(minutes=-30)
    #     after_time = start_time + datetime.timedelta(minutes=30)
    #     queryset = queryset.filter(virtual_class__status=VirtualclassInfo.NOT_START,
    #                                virtual_class__start_time=start_time).filter(virtual_class__start_time)
    #     return queryset


    def status_filter(self, queryset, name, value):
        if value == '0':  # 上岗不隐藏
            queryset = queryset.filter(status=TutorInfo.ACTIVE, working=TutorInfo.WORKING, hide=TutorInfo.DISPLAY)
        elif value == '1':  # 上岗隐藏
            queryset = queryset.filter(status=TutorInfo.ACTIVE, working=TutorInfo.WORKING, hide=TutorInfo.HIDDEN)
        elif value == '2':  # 下岗
            queryset = queryset.filter(status=TutorInfo.ACTIVE, working=TutorInfo.UNWORK)
        elif value == '3':  # 未激活
            queryset = queryset.filter(status=TutorInfo.NOTACTIVE)
        return queryset

    def filter_teacher_name(self, queryset, name, value):
        queryset = queryset.filter(Q(username=value)|Q(email=value)|Q(phone=value)|Q(real_name=value))
        return queryset

    def course_edition_filter(self, queryset, name, value):
        course_level = self.request.query_params.get('course_level')
        if course_level:
            queryset = queryset.filter(tutor_course__course__course_edition_id=value, tutor_course__course__course_level=course_level)
        else:
            queryset = queryset.filter(tutor_course__course__course_edition_id=value)
        return queryset

    def course_level_filter(self, queryset, name, value):
        course_edition = self.request.query_params.get('course_edition')
        if not course_edition:
            queryset = queryset.filter(tutor_course__course__course_level=value)
        return queryset

    def class_type_filter(self, queryset, name, value):
        queryset = queryset.filter(tutor_class_type__class_type_id=value)
        return queryset

    def date_day_filter(self, queryset, name, value):
        if value == 'all':
            now = datetime.datetime.now(tz=utils.tz)
            today = now.strftime('%Y-%m-%d')
            after_seven_time = now + datetime.timedelta(days=6)
            after_seven_date = after_seven_time.strftime('%Y-%m-%d')
            start_date_filter = "DATE(CONVERT_TZ(start_time, '+00:00', '+08:00'))>='{}'".format(today)
            end_date_filter = "DATE(CONVERT_TZ(start_time, '+00:00', '+08:00'))<='{}'".format(after_seven_date)
            date_filter = [start_date_filter, end_date_filter]

        else:  # 没有传值默认查询当前七天
            date_filter = ["DATE(CONVERT_TZ(start_time, '+00:00', '+08:00'))='{}'".format(value)]

        times = self.request.query_params.get('times')
        if times:
            times_list = times.split(',')
            filter_times = []
            for t in times_list:
                filter_times.append("TIME(CONVERT_TZ(start_time, '+00:00', '+08:00'))='{}'".format(t))
            time_filter = ' or '.join(filter_times)
            date_filter.append(time_filter)
        tutor_user_ids = TutorTimetable.objects.filter(status=TutorTimetable.PUBLISHED).extra(where=date_filter).values('tutor_user_id')

        queryset = queryset.filter(id__in=tutor_user_ids)
        return queryset

    class Meta:
        model = TutorInfo
        fields = ['teacher_name', 'course_edition', 'course_level', 'class_type',
                  'date_day', 'status', 'local_area', 'full_work']
