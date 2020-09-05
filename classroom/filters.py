from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, OrderingFilter
from rest_framework import filters
from utils import utils
import datetime
from classroom.models import VirtualclassInfo, ClassType, ClassInfo, VirtualclassComment, ClassMember
from scheduler.models import ScheduleClassTimeTable
from django.utils import timezone
from classroom.config import NEW_STUDENT, OLD_STUDENt
from django.db.models import Q
from student.models import UserStudentInfo
from tutor.models import TutorInfo


class VirtualclassInfoBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        now_time = utils.get_few_date_time()
        search_day = request.query_params.get('search_day', None)
        # appoint_status = request.query_params.get('appoint_status', None)
        teacher = request.query_params.get('teacher', None)
        student = request.query_params.get('student', None)
        if search_day:  # 过滤今天明天后天。。。
            search_day = int(search_day)
            if search_day == 7:
                start, _ = utils.get_day_start_end()
                next_day = utils.get_few_date_time(day=search_day)
                _, end = utils.get_day_start_end(next_day)
                kwargs['start_time' + '__gte'] = start
                kwargs['start_time' + '__lt'] = end
            else:
                next_day = utils.get_few_date_time(day=search_day-1)
                start, end = utils.get_day_start_end(next_day)
                kwargs['start_time' + '__gte'] = start
                kwargs['start_time' + '__lt'] = end
        else:   # 过滤时间段
            start_time = request.query_params.get('start_time', None)
            end_time = request.query_params.get('end_time', None)
            if start_time:
                start_time = "{} 00:00:00".format(start_time)
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utils.tz)
                kwargs['start_time' + '__gte'] = start_time
            if end_time:
                end_time = "{} 23:59:59".format(end_time)
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utils.tz)
                kwargs['start_time' + '__lte'] = end_time

        if teacher:
            if teacher == 'new':  # 过滤新老师
                queryset = queryset.filter(tutor_user__total_number_of_class=0)
            elif teacher == 'old':  # 过滤旧老师
                queryset = queryset.filter(tutor_user__total_number_of_class__gt=0)
        if student:
            if student == NEW_STUDENT:  # 过滤试听课
                queryset = queryset.filter(first_course=VirtualclassInfo.FIRST_COURSE)
            elif student == OLD_STUDENt:  # 过滤正式课
                queryset = queryset.filter(first_course=VirtualclassInfo.NOT_FIRST_COURSE)

        return queryset.filter(**kwargs)


class VirtualclassInfoFilter(FilterSet):

    student_name = CharFilter(method='student_name_filter', label='student_name')
    teacher_name = CharFilter(method='teacher_name_filter', label='teacher_name')
    class_type = NumberFilter('class_type_id')
    class_id = NumberFilter('class_field_id')
    programme_name = NumberFilter(method='programme_name_filter', label='programme_name')
    course_level = NumberFilter(method='course_level_filter', label='course_level')
    cms_user = NumberFilter(method='cms_user_filter', label='cms_user')
    appoint_status = CharFilter(method='appoint_status_filter', label='appoint_status')
    exception = CharFilter(method='exception_filter', label='exception')
    create_user = CharFilter(method='create_user_filter', label='create_user')
    class_no = CharFilter(method='class_no_filter', label='class_no')
    class_name = CharFilter(method='class_name_filter', label='class_name')
    status = NumberFilter('status')
    has_absent_tutor = CharFilter(method='absent_tutor_filter', label='has_absent_tutor')

    def absent_tutor_filter(self, queryset, name, value):
        if value == '1':  # 有被代课老师
            queryset = queryset.filter(absent_tutor_user_id__isnull=False)
        else:
            queryset = queryset.filter(absent_tutor_user_id__isnull=True)
        return queryset

    def class_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(class_field__class_name_zh__icontains=value)|Q(class_field__class_name__icontains=value))
        return queryset

    def class_no_filter(self, queryset, name, value):
        queryset = queryset.filter(class_field__class_no__icontains=value)
        return queryset

    def create_user_filter(self, queryset, name, value):
        queryset = queryset.filter(class_timetable__appoint_user_name__icontains=value)
        return queryset.distinct()

    def student_name_filter(self, queryset, name, value):
        student_list = UserStudentInfo.objects.filter(
            Q(real_name__icontains=value) | Q(parent_user__username__icontains=value) | Q(
                parent_user__email__icontains=value) | Q(parent_user__phone__icontains=value)).only(
            'id').all()[:100]
        student_ids = []
        for student in student_list:
            student_ids.append(student.id)
        if len(student_ids) >= 100:
            queryset = queryset.filter(
                Q(virtual_class_member__student_user__real_name__icontains=value) |
                Q(virtual_class_member__student_user__parent_user__username__icontains=value) |
                Q(virtual_class_member__student_user__parent_user__email__icontains=value) |
                Q(virtual_class_member__student_user__parent_user__phone__icontains=value)).distinct()
        else:
            queryset = queryset.filter(virtual_class_member__student_user_id__in=student_ids)
        return queryset

    def teacher_name_filter(self, queryset, name, value):
        tutor_list = TutorInfo.objects.filter(Q(username__icontains=value)|Q(email__icontains=value)|Q(phone__icontains=value)|Q(real_name__icontains=value)).only('id').all()[:51]
        tutor_ids = []
        for tutor in tutor_list:
            tutor_ids.append(tutor.id)
        if len(tutor_ids) > 50:
            queryset = queryset.filter(Q(tutor_user__username__icontains=value)|Q(tutor_user__email__icontains=value)|Q(tutor_user__phone__icontains=value)|Q(tutor_user__real_name__icontains=value))
        else:
            queryset = queryset.filter(tutor_user_id__in=tutor_ids)
        return queryset

    def appoint_status_filter(self, queryset, name, value):
        if value == 'start':
            queryset = queryset.filter(status=VirtualclassInfo.NOT_START)
        elif value == 'started':
            queryset = queryset.filter(status=VirtualclassInfo.STARTED)
        elif value == 'finish':
            queryset = queryset.filter(status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL))
        return queryset

    def cms_user_filter(self, queryset, name, value):  # 课程顾问跟学管过滤
        queryset = queryset.filter(Q(virtual_class_member__student_user__parent_user__adviser_user_id=value)|Q(virtual_class_member__student_user__parent_user__xg_user_id=value))
        return queryset.distinct()

    def programme_name_filter(self, queryset, name, value):
        queryset = queryset.filter(lesson__course__course_edition_id=value)
        return queryset

    def course_level_filter(self, queryset, name, value):
        queryset = queryset.filter(lesson__course__course_level=value)
        return queryset

    def exception_filter(self, queryset, name, value):

        if value == '1':  # 异常
            queryset = queryset.filter(status=VirtualclassInfo.FINISH_ABNOMAL)
        elif value == '2':  # 正常
            queryset = queryset.filter(status=VirtualclassInfo.FINISH_NOMAL)
        return queryset

    class Meta:
        model = VirtualclassInfo
        fields = ['teacher_name', 'course_level', 'programme_name', 'class_type',
                  'cms_user', 'exception', 'class_id', 'class_name', 'has_absent_tutor']


class HistoryAppointmentFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        kwargs['virtualclass__is_delivered'] = 1
        kwargs['status'] = 0
        search_day = request.query_params.get('search_day', None)
        if search_day:
            few_date = utils.get_few_date_time(int(search_day))
            start, end = utils.get_day_start_end(few_date)
            kwargs['scheduled_time' + '__gte'] = start
            kwargs['scheduled_time' + '__lt'] = end
        else:
            start_time = request.query_params.get('start_time', None)
            end_time = request.query_params.get('end_time', None)
            if start_time:
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                kwargs['scheduled_time' + '__gte'] = start_time
            if end_time:
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                kwargs['scheduled_time' + '__gte'] = end_time
        return queryset.filter(**kwargs)


class ClassInfoFilter(FilterSet):

    # leader_user = CharFilter('leader_user__real_name', lookup_expr='icontains')
    class_name = CharFilter(method='class_name_filter', label='class_name')
    course_edition = NumberFilter('course_edition_id')
    course_level = NumberFilter('course_level')
    create_user = CharFilter('create_user_name', lookup_expr='icontains')
    class_no = CharFilter('class_no', lookup_expr='icontains')
    student_name = CharFilter(method='student_name_filter', label='student_name')
    tutor_name = CharFilter(method='tutor_name_filter', label='tutor_name')
    cms_user = CharFilter(method='cms_user_filter', label='cms_user')

    def cms_user_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(class_member__student_user__parent_user__adviser_user_id=value)|Q(class_member__student_user__parent_user__xg_user_id=value))
        return queryset.distinct()

    def tutor_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(virtualclass_info__tutor_user__username__icontains=value)|Q(virtualclass_info__tutor_user__real_name__icontains=value)).filter(virtualclass_info__status=VirtualclassInfo.NOT_START)
        return queryset.distinct()

    def student_name_filter(self, queryset, name, value):
        queryset = queryset.filter(class_member__student_user__real_name__icontains=value, class_member__role__in=(ClassMember.MEMBER, ClassMember.MONITOR))
        return queryset.distinct()

    def class_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(class_name_zh__icontains=value)|Q(class_name__icontains=value))
        return queryset

    class Meta:
        model = ClassInfo
        fields = ['student_name', 'class_name', 'course_edition', 'course_level', 'create_user', 'class_no',
                  'student_name', 'tutor_name', 'cms_user']


class CommentFilter(FilterSet):

    course_edition = NumberFilter('virtual_class__lesson__course__course_edition_id')
    course_level = NumberFilter('virtual_class__lesson__course__course_level')
    tutor_name = CharFilter(method='tutor_name_filter', label='tutor_name')
    start_date = CharFilter(method='start_date_filter', label='start_date')
    end_date = CharFilter(method='end_date_filter', label='end_date')
    lesson_no = NumberFilter('virtual_class__lesson_no')

    def start_date_filter(self, queryset, name, value):
        start_date_filter = "DATE(CONVERT_TZ(classroom_virtualclass_comment.create_time, '+00:00', '+08:00'))>='{}'".format(value)
        queryset = queryset.extra(where=[start_date_filter])
        return queryset

    def end_date_filter(self, queryset, name, value):
        end_date_filter = "DATE(CONVERT_TZ(classroom_virtualclass_comment.create_time, '+00:00', '+08:00'))<='{}'".format(value)
        queryset = queryset.extra(where=[end_date_filter])
        return queryset

    def tutor_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(tutor_user__username__icontains=value)|Q(tutor_user__email__icontains=value)|Q(tutor_user__phone__icontains=value)|Q(tutor_user__real_name__icontains=value))
        return queryset

    class Meta:
        model = VirtualclassComment
        fields = ['course_edition', 'course_level', 'start_date', 'end_date', 'tutor_name', 'lesson_no']


class ClassTimeTableFilter(FilterSet):

    class_name = CharFilter(method='class_name_filter', label='class_name')
    course_edition = NumberFilter('course_edition_id')
    course_level = NumberFilter('course_level')
    course_edition = NumberFilter('virtual_class__course_edition_id')

    def class_name_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(class_field__class_name_zh__icontains=value)|Q(class_field__class_name_en__icontains=value))
        return queryset

    class Meta:
        model = ScheduleClassTimeTable
        fields = ['class_name', 'course_edition', 'course_level']

