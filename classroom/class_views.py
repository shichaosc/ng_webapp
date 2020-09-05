import logging
from classroom.models import VirtualclassInfo, ClassInfo, ClassType, ClassMember
from scheduler.models import ScheduleClassTimeTable, TutorTimetable
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from utils.pagination import LargeResultsSetPagination
from utils.viewset_base import JsonResponse
from rest_framework.decorators import action
from course.models import CourseLesson, CourseInfo
from django.conf import settings
import requests
from classroom.serializers import ClassInfoSerializer, MatchTutorInfoSerializer
from classroom.class_serializers import ClassTimeTableSerializer, ClassDetailsSerializer, ClassMemberSerializer
from classroom.filters import ClassInfoFilter, ClassTimeTableFilter
from django.db.models import Q, Sum
from django.utils import timezone
from tutor.models import TutorInfo
from datetime import timedelta
from classroom import utils as classroom_utils
from utils import utils, app_settings
from datetime import datetime
import pytz
from functools import cmp_to_key
import random
from users.permissions import IsAuthenticated
from manage.models import UserInfo
from finance.models import AccountBalance
from student.models import UserSource


logger = logging.getLogger('pplingo.ng_webapp.classroom')


class ClassInfoViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = ClassInfoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = ClassInfoFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('user_num', )

    def get_queryset(self):

        start_virtualclass_num = """select count(*) from classroom_virtualclass_info cvi where cvi.class_id=classroom_class_info.id and cvi.status in({}, {})""".format(VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED)

        queryset = ClassInfo.objects.filter(class_type_id__in=(ClassInfo.SMALL_CLASS, ClassInfo.BIG_CLASS)).distinct().all().extra(
            select={
                'finish_num': """select count(*) from classroom_virtualclass_info cvi where cvi.class_id=classroom_class_info.id and cvi.status={}""".format(VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'future_class_sum': start_virtualclass_num
            }
        ).extra(
            select={
                'actual_student_num': """select count(svm.student_user_id) from schedule_virtualclass_member svm left join classroom_virtualclass_info cvi on cvi.id=svm.virtual_class_id where svm.enter_time is not null and cvi.class_id=classroom_class_info.id and cvi.status={}""".format(VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'have_student_num': """select count(svm.student_user_id) from schedule_virtualclass_member svm left join classroom_virtualclass_info cvi on cvi.id=svm.virtual_class_id where cvi.class_id=classroom_class_info.id and cvi.status={}""".format(VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'next_start_time': """select start_time from classroom_virtualclass_info cvi where cvi.class_id=classroom_class_info.id and cvi.status={} order by cvi.start_time limit 1""".format(VirtualclassInfo.NOT_START)
            }
        )
        class_status = self.request.query_params.get('class_status', None)

        if class_status == 1:  # 进行中, 有未上课的virtualclass
            filter_sql = '{}>0'.format(start_virtualclass_num)
            queryset = queryset.extra(
                where=[filter_sql]
            )
        elif class_status == 2:  # 已完结, 没有在上的课
            filter_sql = '{}<=0'.format(start_virtualclass_num)
            queryset = queryset.extra(
                where=[filter_sql]
            )

        return queryset

    @action(methods=['get'], detail=True)
    def details(self, request, pk):

        class_info = ClassInfo.objects.get(id=pk)

        serializers = ClassDetailsSerializer(class_info)

        return JsonResponse(code=0, msg='success', data=serializers.data, status=status.HTTP_200_OK)

    # 修改班级名称
    @action(methods=['put'], detail=True)
    def edite_class_name(self, request, pk):
        class_info = ClassInfo.objects.get(id=pk)
        class_name_zh = request.data.get('class_name_zh')
        class_name = request.data.get('class_name')
        if class_name_zh:
            class_info.class_name_zh = class_name_zh
        if class_name:
            class_info.class_name = class_name
        class_info.save()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 修改班级等级
    @action(methods=['put'], detail=True)
    def edite_class_level(self, request, pk):

        course_edition = request.data.get('course_edition')
        course_level = request.data.get('course_level')
        lesson_no = request.data.get('lesson_no')

        course_info = CourseInfo.objects.filter(course_edition_id=course_edition, course_level=course_level).first()

        if not course_info:
            return JsonResponse(code=1, msg='未找到匹配的课程信息', status=status.HTTP_200_OK)

        course_lesson = CourseLesson.objects.filter(course=course_info, lesson_no=lesson_no, status=CourseLesson.ACTIVE).first()

        if not course_lesson:
            return JsonResponse(code=1, msg='没有该节课', status=status.HTTP_200_OK)

        class_level_url = 'http://' + settings.JAVA_DOMAIN + settings.UPDATE_COURSE_LEVEL.format(class_id=pk, new_edition=course_edition, new_level=course_level, new_lesson_no=lesson_no)

        result = requests.put(class_level_url)

        result = result.json()

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='修改失败', status=status.HTTP_200_OK)
        try:
            user = request.session.get('user')
            logger.debug('{} 修改班级{}等级, class_level_url: {}'.format(user.get('id'), pk, class_level_url))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 创建班级
    @action(methods=['post'], detail=False)
    def create_class(self, request):

        class_name_en = request.data.get('class_name_en')
        class_name_zh = request.data.get('class_name_zh')
        class_type_id = request.data.get('class_type')
        class_category = request.data.get('class_category')
        course_edition_id = request.data.get('course_edition')
        user_max = request.data.get('user_max')
        course_level = request.data.get('course_level')
        unit_no = request.data.get('unit_no')
        lesson_no = request.data.get('lesson_no')
        operation = request.data.get('operation')
        # package_id = request.data.get('package_id')
        student_area = request.data.get('student_area')

        start_time_list = request.data.get('start_times')
        logger.debug(start_time_list)

        lesson = CourseLesson.objects.filter(lesson_no=lesson_no,
                                             unit_no=unit_no,
                                             course__course_level=course_level,
                                             course__course_edition_id=course_edition_id,
                                             status=CourseLesson.ACTIVE).first()
        if not lesson:
            return JsonResponse(code=1, msg='班级课程参数错误', status=status.HTTP_200_OK)

        class_type = ClassType.objects.filter(id=class_type_id).first()

        if not class_type:
            return JsonResponse(code=1, msg='班级规模参数错误', status=status.HTTP_200_OK)

        user = request.session.get('user')

        class_info = ClassInfo()
        class_info.id = random.randint(app_settings.START_ID, app_settings.END_ID)
        class_info.class_no = app_settings.COURSE_EDITION_FLAG.get(course_edition_id, 'XX') + str(random.randint(100000,1000000))
        class_info.class_name = class_name_en
        class_info.class_name_zh = class_name_zh
        class_info.class_type_id = class_type_id
        class_info.class_category = class_category
        class_info.course_edition_id = course_edition_id
        class_info.course_level = course_level
        class_info.lesson = lesson
        class_info.course = lesson.course
        class_info.lesson_no = lesson_no
        # class_info.package_id = package_id
        class_info.student_area = student_area
        if user_max:
            class_info.user_max = user_max
        else:
            class_info.user_max = class_type.user_max
        class_info.first_course = ClassInfo.FIRST_COURSE

        class_info.user_num = 0

        class_info.create_user_id = user.get('id')
        class_info.create_user_name = user.get('realname')
        class_info.save()
        result = self.save_schedule_timetable(request, class_info, user)
        if result:
            try:
                user = request.session.get('user')
                logger.debug('{} 创建班级, class_id: {}'.format(user.get('id'), class_info.id))
            except Exception as e:
                pass
            return JsonResponse(code=0, msg='success', data={'class_id': class_info.id}, status=status.HTTP_200_OK)
        return JsonResponse(code=1, msg='error', status=status.HTTP_200_OK)

    def save_schedule_timetable(self, request, class_info, login_user):

        start_time_list = request.data.get('start_times')

        for start_time in start_time_list:

            start_time = timezone.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
            start_time = start_time - timedelta(hours=8)
            class_time_table = ScheduleClassTimeTable.objects.filter(class_field=class_info, start_time=start_time)\
                .filter(~Q(status=ScheduleClassTimeTable.CANCELD_PUBLISHED)).first()
            if class_time_table:
                continue
            class_time_table = ScheduleClassTimeTable()
            class_time_table.start_time = start_time
            class_time_table.end_time = start_time + timedelta(minutes=app_settings.COURSE_DURATION)
            class_time_table.class_field = class_info
            class_time_table.appoint_user_id = login_user.get('id')
            class_time_table.appoint_user_name = login_user.get('realname')
            class_time_table.status = ScheduleClassTimeTable.PUBLISHED
            class_time_table.save()
            virtual_class = VirtualclassInfo.objects.filter(class_field__id=class_info.id, start_time=class_time_table.start_time, status=VirtualclassInfo.NOT_START).first()

            if virtual_class:
                class_time_table.status = ScheduleClassTimeTable.SUCCESS_APPOINTMENT
                class_time_table.virtual_class_id = virtual_class.id
                class_time_table.save()

        return 1

    def add_adviser_user_name(self, data):
        user_info_ids = []
        for d in data:
            adviser_user_id = d.get('student_user').get('parent_user').get('adviser_user_id')
            xg_user_id = d.get('student_user').get('parent_user').get('xg_user_id')
            if adviser_user_id and adviser_user_id not in user_info_ids:
                user_info_ids.append(adviser_user_id)
            if xg_user_id and xg_user_id not in user_info_ids:
                user_info_ids.append(xg_user_id)

        user_infos = UserInfo.objects.filter(id__in=user_info_ids).all().only('id', 'realname')
        user_info_dict = {}
        for user_info in user_infos:
            user_info_dict[user_info.id] = user_info
        for s in data:
            adviser_instance = user_info_dict.get(s.get('student_user').get('parent_user').get('adviser_user_id'))
            if adviser_instance:
                s.get('student_user').get('parent_user')['adviser_user_name'] = adviser_instance.realname
            else:
                s.get('student_user').get('parent_user')['adviser_user_name'] = None
            xg_instance = user_info_dict.get(s.get('student_user').get('parent_user').get('xg_user_id'))
            if xg_instance:
                s.get('student_user').get('parent_user')['xg_user_name'] = xg_instance.realname
            else:
                s.get('student_user').get('parent_user')['xg_user_name'] = None
        return data

    def add_account_balance(self, data):
        parent_user_ids = []
        for d in data:
            parent_user_id = d.get('student_user').get('parent_user').get('id')
            if parent_user_id and parent_user_id not in parent_user_ids:
                parent_user_ids.append(parent_user_id)
        account_balances = AccountBalance.objects.filter(parent_user_id__in=parent_user_ids, state=AccountBalance.NOT_DELETE).values('parent_user_id', 'account_class').annotate(balance_sum=Sum('balance')).values('parent_user_id', 'account_class', 'balance_sum')
        account_balance_dict = {}
        for account_balance in account_balances:
            parent_user_id = account_balance.get('parent_user_id')
            account_class = account_balance.get('account_class')
            balance_sum = account_balance.get('balance_sum')
            if parent_user_id in account_balance_dict.keys():
                if account_class == AccountBalance.NORMAL_ACCOUNT:
                    account_balance_dict[parent_user_id]["normal_balance"] = balance_sum
                elif account_class == AccountBalance.PRIVATE_ACCOUNT:
                    account_balance_dict[parent_user_id]["sg_balance"] = balance_sum
            else:
                account_balance_dict[parent_user_id] = {}
                if account_class == AccountBalance.NORMAL_ACCOUNT:
                    account_balance_dict[parent_user_id]["normal_balance"] = balance_sum
                elif account_class == AccountBalance.PRIVATE_ACCOUNT:
                    account_balance_dict[parent_user_id]["sg_balance"] = balance_sum

        for d in data:
            parent_user_id = d.get('student_user').get('parent_user').get('id')
            account_balance_info = account_balance_dict.get(parent_user_id, {})
            d.get('student_user').get('parent_user')['normal_balance'] = account_balance_info.get('normal_balance', 0)
            d.get('student_user').get('parent_user')['sg_balance'] = account_balance_info.get('sg_balance', 0)
        return data

    def add_user_source(self, data, activity_code):
        if activity_code == 'bigclass':
            for d in data:
                d.get('student_user').get('parent_user')['user_source'] = 'bigclass'
            return data
        elif activity_code == 'other':
            for d in data:
                d.get('student_user').get('parent_user')['user_source'] = ''
            return data
        parent_user_ids = []
        for d in data:
            parent_user_id = d.get('student_user').get('parent_user').get('id')
            if parent_user_id and parent_user_id not in parent_user_ids:
                parent_user_ids.append(parent_user_id)
        big_class_parent_user_ids = UserSource.objects.filter(parent_user_id__in=parent_user_ids, activity_code=activity_code).all().values('parent_user_id')
        big_class_parent_user_list = []
        for big_class_parent_user_id in big_class_parent_user_ids:
            big_class_parent_user_list.append(big_class_parent_user_id.get('parent_user_id'))
        for d in data:
            parent_user_id = d.get('student_user').get('parent_user').get('id')
            if parent_user_id in big_class_parent_user_list:
                d.get('student_user').get('parent_user')['user_source'] = 'bigclass'
            else:
                d.get('student_user').get('parent_user')['user_source'] = ''
        return data

    # 班级成员
    @action(methods=['get'], detail=True)
    def class_members(self, request, pk):
        student_name = request.query_params.get('student_name')
        activity_code = request.query_params.get('user_source')
        try:
            class_info = ClassInfo.objects.get(id=pk)
        except Exception as e:
            logger.debug('查询班级成员出错,class_id={}, error={}'.format(pk, e))
            return JsonResponse(code=1, msg='未查询到班级', status=status.HTTP_200_OK)
        members = ClassMember.objects.filter(class_field=class_info, role__in=(ClassMember.MONITOR, ClassMember.MEMBER)).all()

        members = members.select_related('student_user').select_related('student_user__parent_user').only(
            'id', 'student_user_id', 'create_time',
            'student_user__id', 'student_user__real_name', 'student_user__gender', 'student_user__birthday', 'student_user__create_time',
            'student_user__parent_user__id', 'student_user__parent_user__username', 'student_user__parent_user__country_of_residence', 'student_user__parent_user__adviser_user_id')
        members = members.order_by('-create_time')

        if student_name:
            members = members.filter(Q(student_user__real_name__icontains=student_name)|Q(student_user__parent_user__username__icontains=student_name)|Q(student_user__parent_user__email__icontains=student_name)|Q(student_user__parent_user__phone__icontains=student_name))

        if activity_code == 'bigclass':
            members = members.filter(student_user__parent_user__user_source__activity_code=activity_code)
            print(members.query)
        elif activity_code == 'other':
            members = members.filter(Q(student_user__parent_user__user_source__isnull=True)|~Q(student_user__parent_user__user_source__activity_code='bigclass'))

        page = LargeResultsSetPagination()
        page_roles = page.paginate_queryset(queryset=members, request=request, view=self)
        members_sreializer = ClassMemberSerializer(instance=page_roles, many=True)
        data = self.add_adviser_user_name(members_sreializer.data)
        data = self.add_account_balance(data)
        data = self.add_user_source(data, activity_code)
        # return Response(roles_ser.data)  # 只返回数据
        return page.get_paginated_response(data)  # 返回前后夜url

    # 添加班级成员
    @action(methods=['put'], detail=True)
    def add_class_member(self, request, pk):
        student_id = request.data.get('student_id')
        if not student_id:
            return JsonResponse(code=1, msg='参数缺失', status=status.HTTP_200_OK)
        data = {
            "classId": pk,
            "userId": student_id
        }
        url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_ADD_CLASS
        result = utils.fetch_post_api(url, data)
        if result.get('code') != 200:
            return JsonResponse(code=1, msg='添加失败,{}'.format(result.get('message', '')),  data=result.get('data', []), status=status.HTTP_200_OK)
        try:
            user = request.session.get('user')
            logger.debug('{} 添加班级成员, class_id: {}, student_id: {}'.format(user.get('id'), pk, student_id))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 移出班级成员
    @action(methods=['put'], detail=True)
    def remove_class_member(self, request, pk):

        student_id = request.data.get('student_id')

        remove_class_student_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDNT_SIGN_OUT_CLASS.format(class_id=pk, student_user_id=student_id)

        headers = {
            'content-type': 'application/json'
        }

        result = requests.delete(remove_class_student_url, headers=headers)

        result = result.json()

        if result.get('code') != 200:
            logger.debug(result)
            return JsonResponse(code=1, msg='移出失败, {}'.format(result.get('message', '')), status=status.HTTP_200_OK)
        try:
            user = request.session.get('user')
            logger.debug('{} 移出班级成员, class_id: {}, student_id: {}'.format(user.get('id'), pk, student_id))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 批量加入班级成员
    @action(methods=['post'], detail=False)
    def add_student_batch(self, request):

        data_textarea = request.data.get('data_textarea')
        class_no = request.data.get('class_no')

        datas = data_textarea.split('\n')
        post_data = []
        fail_data = []
        for data in datas:
            try:
                '''账号,学生名字,学生性别,学生生日,课程顾问,学管'''
                student_data = data.split(',')
                adviser_user_name = student_data[4].strip()
                adviser_user = UserInfo.objects.filter(realname=adviser_user_name).first()
                xg_user_name = student_data[5].strip()
                xg_user = UserInfo.objects.filter(realname=xg_user_name).first()
                gender = student_data[2].strip()
                if gender == '男孩':
                    student_gender = 1
                elif gender == '女孩':
                    student_gender = 2
                else:
                    student_gender = 0
                age = student_data[3].strip()  # 年龄 换算成生日
                now_time = timezone.now()
                birthday = now_time.replace(now_time.year-int(age))
                birthday = birthday.strftime('%Y-%m-%d')
                data = {
                    "adviserUserName": "",
                    "adviserUserPhone": "",
                    "childBirthday": birthday + 'T00:00:00.000Z',
                    "childGender": student_gender,
                    "childRealName": student_data[1].strip(),
                    "classNo": class_no,
                    "parentIdentify": student_data[0].strip(),
                    "xgUserName": "",
                    "xgUserPhone": ""
                }
                if adviser_user:
                    data['adviserUserId'] = adviser_user.id
                    data['adviserUserName'] = adviser_user.realname
                    data['adviserUserPhone'] = adviser_user.phone
                if xg_user:
                    data['xgUserId'] = xg_user.id
                    data['xgUserName'] = xg_user.realname
                    data['xgUserPhone'] = xg_user.phone
                post_data.append(data)
            except Exception as e:
                logger.debug('add_student_batch fail, error={}'.format(e))
                fail_data.append(data)
        logger.debug('add_student_batch data={}'.format(post_data))
        student_join_class_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_JOIN_CLASS

        return_result = utils.fetch_post_api(student_join_class_url, post_data)

        result = {
            'fail_data': fail_data,
            'return_data': return_result
        }

        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)


class ClassTimeTableViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = ClassTimeTableSerializer
    filter_class = ClassTimeTableFilter
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):

        queryset = ScheduleClassTimeTable.objects.all().select_related('virtual_class').select_related('virtual_class__tutor_user')

        return queryset

    # 小班课上课时间
    @action(methods=['get'], detail=True)
    def all(self, request, pk):
        # class_info = ClassInfo.objects.get(id=class_id)
        now_time = timezone.now()
        class_timetables = ScheduleClassTimeTable.objects.filter(class_field_id=pk, start_time__gt=now_time,
                                                                 status__in=(ScheduleClassTimeTable.SUCCESS_APPOINTMENT,
                                                                             ScheduleClassTimeTable.PUBLISHED)).all().order_by('start_time')

        for class_timetable in class_timetables:
            if class_timetable.virtual_class:
                if class_timetable.virtual_class.status == VirtualclassInfo.CANCELED:
                    class_timetable.status = VirtualclassInfo.CANCELED
                    class_timetable.save()

        serializers = ClassTimeTableSerializer(class_timetables, many=True)
        return JsonResponse(code=0, msg='success', data=serializers.data, status=status.HTTP_200_OK)

    # 匹配老师
    @action(methods=['get'], detail=False)
    def match_teacher(self, request):

        start_time_list = request.query_params.getlist('start_times[]', [])
        class_id = request.query_params.get('class_id')
        tutor_status = request.query_params.get('tutor_status', '')
        full_work = request.query_params.get('full_work', '')
        query_times = []

        for start_time in start_time_list:
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').astimezone(pytz.UTC)
            start_time = start_time - timedelta(hours=8)
            before_time = start_time + timedelta(minutes=-30)
            after_time = start_time + timedelta(minutes=30)
            query_times.extend([start_time, before_time, after_time])

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        tutor_name = request.query_params.get('tutor_name')

        tutor_queryset = TutorInfo.objects.filter(status=TutorInfo.ACTIVE, working=TutorInfo.WORKING, tutor_class_type__class_type_id=ClassType.SMALLCLASS)

        if tutor_status == '0':  # 上岗不隐藏
            tutor_queryset = tutor_queryset.filter(hide=TutorInfo.DISPLAY)
        elif tutor_status == '1':  # 上岗隐藏
            tutor_queryset = tutor_queryset.filter(hide=TutorInfo.HIDDEN)

        if full_work == '0':
            tutor_queryset = tutor_queryset.filter(full_work=0)
        elif full_work == '1':
            tutor_queryset = tutor_queryset.filter(full_work=1)

        if tutor_name:
            tutor_queryset = tutor_queryset.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)|Q(real_name=tutor_name))

        if class_id:
            class_info = ClassInfo.objects.get(id=class_id)
            tutor_queryset = tutor_queryset.filter(tutor_course__course_id=class_info.lesson.course_id)

        tutor_list = tutor_queryset.values_list('id')
        sort_result = []

        # 查出所有的约课记录
        timetables = TutorTimetable.objects.filter(start_time__in=query_times,
                                                   status__in=(TutorTimetable.PUBLISHED,
                                                               TutorTimetable.SUCCESS_APPOINTMENT)).values(
            'tutor_user_id', 'start_time', 'status')
        timetable_dict = {}
        for timetable in timetables:
            tutor_user_id = timetable.pop('tutor_user_id')
            if tutor_user_id in timetable_dict.keys():
                timetable_dict[tutor_user_id].append(timetable)
            else:
                timetable_dict[tutor_user_id] = []
                timetable_dict[tutor_user_id].append(timetable)

        for tutor_id in tutor_list:
            tutor_id = tutor_id[0]
            publish_count = 0
            no_publish_count = 0
            # timetables = timetable_dict.get(tutor_id, [])
            sort_dict = {}
            publish_time_list = []
            appointment_time_list = []
            conflict_times = []  # 冲突时间
            for timetable in timetable_dict.get(tutor_id, []):
                if timetable.get('status') == TutorTimetable.SUCCESS_APPOINTMENT:
                    appointment_time_list.append(timetable.get('start_time'))
                else:
                    publish_time_list.append(timetable.get('start_time'))

            for query_time in start_time_list:
                query_time = datetime.strptime(query_time, '%Y-%m-%d %H:%M:%S').astimezone(pytz.UTC)
                query_time = query_time - timedelta(hours=8)
                before_query_time = query_time + timedelta(minutes=-30)
                after_query_time = query_time + timedelta(minutes=30)

                result = list(set([query_time, before_query_time, after_query_time]).intersection(set(appointment_time_list)))

                if result:
                    conflict_times.append(query_time.strftime('%Y-%m-%d %H:%M:%S'))
                    continue
                else:
                    if query_time in publish_time_list:
                        publish_count = publish_count + 1
                    else:
                        no_publish_count = no_publish_count + 1
            sort_dict['tutor_user_id'] = tutor_id
            sort_dict['publish_count'] = publish_count
            sort_dict['no_publish_count'] = no_publish_count
            sort_dict['conflict_times'] = conflict_times

            sort_result.append(sort_dict)

        tutor_sum = len(sort_result)

        sort_result = sorted(sort_result, key=cmp_to_key(classroom_utils.cmp_tutor_match))
        sort_result = sort_result[(page-1)*page_size:page_size*page]

        if not sort_result:
            return JsonResponse(code=0, msg='success', data={'count': tutor_sum, 'data': []}, status=status.HTTP_200_OK)

        tutor_publish_dict = {tutor_dict.get('tutor_user_id'): tutor_dict for tutor_dict in sort_result}

        tutor_ids = ','.join([str(tutor_dict.get('tutor_user_id')) for tutor_dict in sort_result])

        month_ago = timezone.now() - timedelta(days=30)  # 30天之内的学生

        tutors = TutorInfo.objects.raw(
            '''SELECT (select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                        left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                        WHERE cvi.tutor_user_id = user_tutor_info.id AND cvi.start_time >= '{}' AND cvi.STATUS IN ( {}, {}, {} ) ) AS `student_count`,
                        `user_tutor_info`.`id`,
                        `user_tutor_info`.`role`,
                        `user_tutor_info`.`username`,
                        `user_tutor_info`.`phone`,
                        `user_tutor_info`.`email`,
                        `user_tutor_info`.`password`,
                        `user_tutor_info`.`avatar`,
                        `user_tutor_info`.`real_name`,
                        `user_tutor_info`.`gender`,
                        `user_tutor_info`.`birthday`,
                        `user_tutor_info`.`nationality`,
                        `user_tutor_info`.`country_of_residence`,
                        `user_tutor_info`.`status`,
                        `user_tutor_info`.`working`,
                        `user_tutor_info`.`hide`,
                        `user_tutor_info`.`identity_name`
                        FROM
                            `user_tutor_info` 
                        WHERE
                            `user_tutor_info`.`id` IN ({}) 
                        ORDER BY
                             find_in_set(user_tutor_info.id, "{}") 
                             '''.format(utils.datetime_str(month_ago), VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED, VirtualclassInfo.FINISH_NOMAL, tutor_ids, tutor_ids)
                                )

        serializers = MatchTutorInfoSerializer(tutors, many=True, context={"tutor_publish_dict": tutor_publish_dict})

        return JsonResponse(code=0, msg='success', data={'count': tutor_sum, 'data':serializers.data}, status=status.HTTP_200_OK)

    # 安排老师 约课
    @action(methods=['post'], detail=False)
    def subscribe(self, request):

        class_timetable_ids = request.data.get('class_timetable_ids')
        tutor_user_id = request.data.get('tutor_user_id')

        class_timetables = ScheduleClassTimeTable.objects.filter(id__in=class_timetable_ids).all()

        start_times, end_times = [], []
        class_id = None
        class_type_id = None
        for class_timetable in class_timetables:
            start_times.append(class_timetable.start_time)
            end_times.append(class_timetable.end_time)
            class_id = class_timetable.class_field_id
            class_type_id = class_timetable.class_field.class_type_id

        subscribe_url = 'http://' + settings.JAVA_DOMAIN + settings.SCHEDULE_SUBSCRIBE

        user = request.session.get('user')

        data = {
            "classId": class_id,
            "classTypeId": class_type_id,
            "endTimes": end_times,
            "opType": 1,  # 1：预约时间；2：取消预约
            "startTimes": start_times,
            "tutorUserId": tutor_user_id,
            "opUserId": user.get('id')
        }

        result = utils.fetch_post_api(subscribe_url, data, user_id=user.get('id'))

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='约课失败, {}'.format(result.get('message', '')), data=result.get('data', []), status=status.HTTP_200_OK)

        for class_timetable in class_timetables:
            virtual_class = VirtualclassInfo.objects.filter(class_field_id=class_timetable.class_field_id, start_time=class_timetable.start_time, status=VirtualclassInfo.NOT_START).first()
            class_timetable.virtual_class = virtual_class
            class_timetable.status = ScheduleClassTimeTable.SUCCESS_APPOINTMENT
            class_timetable.appoint_user_id = user.get('id')
            class_timetable.appoint_user_name = user.get('realname')
            class_timetable.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 取消课程
    @action(methods=['post'], detail=False)
    def cancle_timetable(self, request):

        class_timetable_ids = request.data.get('class_timetable_ids')

        class_time_tables = ScheduleClassTimeTable.objects.filter(id__in=class_timetable_ids).all()

        start_times, end_times = [], []
        class_id = None
        class_type_id = None

        user = request.session.get('user')

        for class_timetable in class_time_tables:

            if class_timetable.status == ScheduleClassTimeTable.SUCCESS_APPOINTMENT:

                start_times.append(class_timetable.start_time)
                end_times.append(class_timetable.end_time)
                class_id = class_timetable.class_field_id
                class_type_id = class_timetable.class_field.class_type_id

        if start_times:
            cancel_url = 'http://' + settings.JAVA_DOMAIN + settings.SCHEDULE_SUBSCRIBE

            data = {
                "classId": class_id,
                "classTypeId": class_type_id,
                "endTimes": end_times,
                "opType": 2,  # 1：预约时间；2：取消预约
                "startTimes": start_times,
                "tutorUserId": 0,
                "opUserId": user.get('id')
            }

            result = utils.fetch_post_api(cancel_url, data, user_id=user.get('id'))

            if result.get('code') != 200:
                return JsonResponse(code=1, msg='取消课程失败, {}'.format(result.get('message', '')), data=result.get('data', []), status=status.HTTP_200_OK)

        for class_timetable in class_time_tables:
            class_timetable.appoint_user_id = user.get('id')
            class_timetable.appoint_user_name = user.get('realname')
            class_timetable.status = ScheduleClassTimeTable.CANCELD_PUBLISHED
            class_timetable.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 预排课
    @action(methods=['post'], detail=False)
    def schedule_timetable(self, request):

        class_id = request.data.get('class_id')
        start_time_list = request.data.get('start_times')

        class_info = ClassInfo.objects.filter(id=class_id).first()
        if not class_info:
            return JsonResponse(code=1, msg='未找到该班级', status=status.HTTP_200_OK)

        user = request.session.get('user')

        for start_time in start_time_list:

            start_time = timezone.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
            start_time = start_time - timedelta(hours=8)
            class_time_table = ScheduleClassTimeTable.objects.filter(class_field=class_info, start_time=start_time)\
                .filter(~Q(status=ScheduleClassTimeTable.CANCELD_PUBLISHED)).first()
            if class_time_table:
                continue
            class_time_table = ScheduleClassTimeTable()
            class_time_table.start_time = start_time
            class_time_table.end_time = start_time + timedelta(minutes=app_settings.COURSE_DURATION)
            class_time_table.class_field = class_info
            class_time_table.appoint_user_id = user.get('id')
            class_time_table.appoint_user_name = user.get('realname')
            class_time_table.status = ScheduleClassTimeTable.PUBLISHED
            class_time_table.save()

            virtual_class = VirtualclassInfo.objects.filter(class_field__id=class_info.id, start_time=class_time_table.start_time, status=VirtualclassInfo.NOT_START).first()

            if virtual_class:
                class_time_table.status = ScheduleClassTimeTable.SUCCESS_APPOINTMENT
                class_time_table.virtual_class_id = virtual_class.id
                class_time_table.save()

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 更换老师
    @action(methods=['post'], detail=False)
    def change_tutor(self, request):

        class_timetable_ids = request.data.get('class_timetable_ids')

        tutor_user_id = request.data.get('tutor_user_id')

        class_timetables = ScheduleClassTimeTable.objects.filter(id__in=class_timetable_ids, status=ScheduleClassTimeTable.SUCCESS_APPOINTMENT).all()

        end_times = []
        start_times = []
        class_id = None
        class_type_id = None

        user = request.session.get('user')

        for class_timetable in class_timetables:
            start_times.append(class_timetable.start_time)
            end_times.append(class_timetable.end_time)
            class_id = class_timetable.class_field_id
            class_type_id = class_timetable.class_field.class_type_id

        if start_times:
            change_tutor_url = 'http://' + settings.JAVA_DOMAIN + settings.SCHEDULE_CHANGE_TUTOR

            data = {
                    "classId": class_id,
                    "classTypeId": class_type_id,
                    "endTimes": end_times,
                    "startTimes": start_times,
                    "tutorUserId": tutor_user_id
                }

            result = utils.fetch_post_api(change_tutor_url, data, user_id=user.get('id'))

            if result.get('code') != 200:
                return JsonResponse(code=1, msg='更换老师失败, {}'.format(result.get('message', '')), status=status.HTTP_200_OK)

        for class_timetable in class_timetables:
            virtual_class = VirtualclassInfo.objects.filter(class_field_id=class_timetable.class_field_id,
                                                            start_time=class_timetable.start_time,
                                                            status=VirtualclassInfo.NOT_START).first()
            class_timetable.virtual_class = virtual_class
            class_timetable.status = ScheduleClassTimeTable.SUCCESS_APPOINTMENT
            class_timetable.appoint_user_id = user.get('id')
            class_timetable.appoint_user_name = user.get('realname')
            class_timetable.save()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)
