import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from course.models import CourseEdition, CourseInfo
from tutor.models import TutorInfo, UserLevel
from finance.models import BalanceChange, TutorSalary, BalanceChangeNew
from classroom.models import ClassType, VirtualclassInfo
from scheduler.models import ScheduleTutorLevel, TutorTimetable
from django.http import HttpResponse
from django.utils import timezone
from common.models import ExchangeRate
from ng_webapp import utils
from decimal import Decimal
from tutor.serializer import TutorVirtualclassSerializer, MatchTutorInfoSerializer
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework import viewsets, status
from tutor.serializer import TeacherListSerializer
from utils.pagination import TeacherPagination
from tutor.filters import TeacherFilter
from tutor.models import TutorInfo
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta, datetime
from utils import utils
import pytz
from users.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.conf import settings
from utils.viewset_base import JsonResponse
from student.models import UserStudentInfo
import logging

logger = logging.getLogger('pplingo.ng_webapp.course')

@login_required
def list_all_tutors(request):

    programmes = CourseEdition.objects.all()

    programme_ids = request.GET.get('programme_ids', [])
    tutor_status = request.GET.get('tutor_status', [])

    tutors = TutorInfo.objects.all().distinct()

    if programme_ids:
        programme_ids = programme_ids.split(',')
        tutors = tutors.filter(tutor_course__course__course_edition__id__in=programme_ids)

    if tutor_status:
        tutor_status = tutor_status.split(',')
        search_list = []
        for status in tutor_status:
            if int(status) == 0:  # 上岗
                query = 'Q(hide=0, working=1, status=1)'
            elif int(status) == 1:  # 仅老生可见
                query = 'Q(hide=1, working=1, status=1)'
            elif int(status) == 2:  # 离岗
                query = 'Q(working=0, status=1)'
            elif int(status) == 3:  # 未激活
                query = 'Q(status=0)'
            search_list.append(query)
        tutors = tutors.filter(eval('|'.join(search_list)))
    '''
    # This query will retrieve userprofile-avatar onetime together with tutor list
    tutors = Tutor.objects.extra(
                                 select={
        'avatar': 'SELECT avatar FROM userprofile_userprofile WHERE userprofile_userprofile.user_id = tutor_tutor.user_id'
    },)
    '''
    try:
        cur_programme = [int(programme_id) for programme_id in programme_ids]
        if tutor_status:
            tutor_status = [int(status) for status in tutor_status]
    except:
        cur_programme = []
        tutor_status = tutor_status
    if not tutor_status:
        tutor_status = []
    logger.debug("*****************************")
    logger.debug(tutor_status)
    logger.debug(cur_programme)
    return render(request,
                  'tutor/all_tutors.html',
                  {'programmes': programmes,
                   'tutors': tutors,
                   'cur_programme': cur_programme,
                   'tutor_status': tutor_status
                   })


@login_required
def management(request):
    # tutors = TutorInfo.objects.all()
    programmes = CourseEdition.objects.all()
    courses = CourseInfo.objects.all()
    class_type = ClassType.objects.all()
    grades = UserLevel.objects.all()
    content = {'courses': courses, 'class_type': class_type, 'grades': grades, 'programmes': programmes}
    return render(request, 'man/tutor/management.html', content)


# @login_required
def tutor_grade_add(request):

    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'status': 2, 'message': '登陆信息过期，请重新登陆'}))

    tutor_grade = request.POST.get('tutor_grade')
    tutor_name = request.POST.get('tutor_name')
    tutor_grade = json.loads(tutor_grade)

    tutor = TutorInfo.objects.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)).first()

    if not tutor:
        return HttpResponse(json.dumps({'status': 1, 'message': '未找到该老师'}))

    for grade_info in tutor_grade:
        course_edition_id = grade_info.get('programme')
        level = grade_info.get('grade')
        if not level or not course_edition_id:
            continue
        tutor_level = ScheduleTutorLevel.objects.filter(course_edition__id=course_edition_id, tutor_user=tutor).first()
        if tutor_level:
            tutor_level.user_level_id = level
            tutor_level.save()
        else:
            tutor_level = ScheduleTutorLevel()
            tutor_level.course_edition_id = course_edition_id
            tutor_level.user_level_id = level
            tutor_level.tutor_user = tutor
            tutor_level.save()
        logger.debug('change tutor level, tutor_user_id: {}, operate_user_id:{}, operate_user_name: {}, course_edition_id: {}, user_level_id: {}'.format(tutor.id, request.user.id, request.user.username, course_edition_id, level))
    return HttpResponse(json.dumps({'status': 0, 'message': 'success'}))


@login_required
def tutor_salary(request):
    data_date = request.GET.get('data_date')
    if not data_date:
        now_time = utils.utc_time_to_beijing(timezone.now())
        data_date = now_time.strftime('%Y%m')

    tutor_salarys = TutorSalary.objects.filter(data_date=data_date).all().select_related('tutor_user')

    tutor_count = tutor_salarys.count()
    tutor_salary_sum_cny = 0
    tutor_salary_sum_sgd = 0
    result = []
    for tutor_salary in tutor_salarys:

        tutor_user = tutor_salary.tutor_user
        if not tutor_user:
            continue
        tutor_dict = {}
        # tutor_dict['id'] = tutor.get('id')
        tutor_dict['user_id'] = tutor_user.id
        tutor_dict['username'] = tutor_user.__str__()
        tutor_dict['real_name'] = tutor_user.real_name
        tutor_dict['lesson_num'] = tutor_salary.lesson_num
        tutor_dict['salary'] = tutor_salary.base_salary + tutor_salary.incentive_salary + tutor_salary.student_absence_salary + tutor_salary.tutor_absence_salary
        tutor_dict['student_num'] = tutor_salary.student_num
        tutor_dict['pay_status'] = tutor_salary.pay_status
        tutor_dict['currency'] = tutor_salary.currency
        tutor_dict['card_name'] = tutor_user.identity_name   # 身份证名称
        tutor_dict['card_number'] = tutor_user.identity_number  # 身份证号
        tutor_dict['bank_account_number'] = tutor_user.bank_account_number  # 银行卡号
        tutor_dict['bank_name'] = tutor_user.bank_name   # 开户行
        tutor_dict['bank_branch_name'] = tutor_user.bank_branch_name  # 开户行支行
        if tutor_salary.currency == ExchangeRate.default_currency:
            tutor_salary_sum_cny = tutor_salary_sum_cny + Decimal(str(tutor_dict['salary']))
        else:
            tutor_salary_sum_sgd = tutor_salary_sum_sgd + Decimal(str(tutor_dict['salary']))
        result.append(tutor_dict)
    return render(request, 'man/tutor/tutor_salary.html', {'tutor_salary': result,
                                                           'tutor_count': tutor_count,
                                                           'tutor_salary_sum_cny': tutor_salary_sum_cny,
                                                           'tutor_salary_sum_sgd': tutor_salary_sum_sgd,
                                                           'data_date': data_date})


# @login_required
def update_pay_status(request):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'status': 2, 'message': '登陆信息过期，请重新登陆'}))
    teacher_ids = request.POST.getlist('teacher_ids')
    teacher_ids = [int(teacher_id) for teacher_id in teacher_ids]
    data_date = request.POST.get('data_date', '')
    now_time = timezone.now()
    # 获得工资基数
    rate = ExchangeRate.objects.filter(currency=ExchangeRate.default_currency, valid_start__lte=now_time, valid_end__gt=now_time)
    exchange_rate = rate.first().rate

    singapore_rate = ExchangeRate.objects.filter(currency='SGD', valid_start__lte=now_time, valid_end__gt=now_time)
    singapore_exchange_rate = singapore_rate.first().rate
    salarys = TutorSalary.objects.filter(tutor_user_id__in=teacher_ids, data_date=data_date).select_related('tutor_user').all()

    for salary in salarys:
        if salary.pay_status == TutorSalary.UNPAY:
            tutor_user = salary.tutor_user
            if salary.currency == 'SGD':
                exchange_rate = singapore_exchange_rate
            amount = salary.base_salary + salary.incentive_salary + salary.student_absence_salary + salary.tutor_absence_salary
            amount = 0 - Decimal(amount) / exchange_rate
            # 支付工资记录 同时修改教师账户
            a_b_c = BalanceChangeNew(user_id=tutor_user.id, amount=amount, reason=BalanceChange.WITHDRAW, role=BalanceChange.TEACHER,
                                         reference=salary.data_date)
            a_b_c.save()
            tutor_user.balance = tutor_user.balance + a_b_c.amount
            tutor_user.save()
            salary.pay_status = TutorSalary.PAYMENTED
            salary.pay_user_id = request.user.id
            a_b_c.save()
            salary.save()
    logger.debug('update pay status, operate_user_id: {}, data_date: {}'.format(request.user.id, data_date))
    # for teacher_id in teacher_ids:
    #     salary = TutorSalary.objects.filter(tutor_user_id=teacher_id, data_date=data_date).first()
    #     if salary.pay_status == TutorSalary.UNPAY:
    #         if salary.currency == 'SGD':
    #             exchange_rate = singapore_exchange_rate
    #         amount = salary.base_salary + salary.incentive_salary + salary.student_absence_salary + salary.tutor_absence_salary
    #         amount = 0 - Decimal(amount) / exchange_rate
    #         # 支付工资记录 同时修改教师账户
    #         a_b_c = BalanceChange(user_id=teacher_id, amount=amount, reason=BalanceChange.WITHDRAW, role=BalanceChange.TEACHER,
    #                                      reference=salary.data_date)
    #         salary.pay_status = TutorSalary.PAYMENTED
    #         salary.pay_user_id = request.user.id
    #         a_b_c.save()
    #         salary.save()
    return HttpResponse(json.dumps({'status': 0, 'message': 'success'}))


# @login_required
def tutor_salary_order(request):
    teacher_id = request.POST.get('teacher_id')
    order_no = request.POST.get('order_no')
    data_date = request.POST.get('data_date')
    if not teacher_id or not order_no or not data_date:
        return HttpResponse(json.dumps({'status': 1, 'message': '参数缺失'}))
    now_time = timezone.now()
    TutorSalary.objects.filter(user_id=teacher_id, data_date=data_date).update(order_no=order_no, update_time=now_time, pay_user=request.user)
    return HttpResponse(json.dumps({'status': 0, 'message': 'success'}))


# @login_required
def tutor_salary_detail(request):
    teacher_id = request.GET.get('teacher_id')
    data_date = request.GET.get('data_date')
    if not teacher_id or not data_date:
        return HttpResponse(json.dumps({'status': 1, 'message': '参数缺失'}))

    year, month = data_date[:4], data_date[4:]

    start_time, end_time = utils.get_start_end_month(year, month)

    #判断是不是本月
    now_time = timezone.now().astimezone(tz=utils.tz)
    now_date = now_time.strftime('%Y%m')
    if data_date == now_date:
        end_time = now_time

    virtualclass = VirtualclassInfo.objects.filter(tutor_user_id=teacher_id,
                                                   start_time__lte=end_time,
                                                   start_time__gte=start_time,
                                                   status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL)).order_by('start_time')
    virtualclass = virtualclass.select_related('tutor_user').select_related('lesson').select_related('lesson__course').select_related('lesson__course__course_edition').prefetch_related('virtual_class_member').prefetch_related('virtual_class_member__student_user')
    tutor_salary = TutorSalary.objects.filter(tutor_user_id=teacher_id, data_date=data_date).first()

    if not tutor_salary:
        tutor_salary = {}
    else:
        tutor_salary = model_to_dict(tutor_salary)

    serializer = TutorVirtualclassSerializer(virtualclass, many=True)
    result = []
    for r in serializer.data:
        res = {}
        res['studentname'] = r.get('studentname')
        res['scheduled_time'] = r.get('scheduled_time')
        res['programme_name'] = r.get('programme_name')
        res['course_level'] = r.get('course_level')
        res['course_session'] = r.get('course_session')
        res['salary'] = r.get('salary')
        result.append(res)

    data = {
        'tutor_salary': tutor_salary,
        'tutor_detail': result
    }
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))


# @login_required
def set_tutor_status(request):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'status': 2, 'message': '登陆信息过期，请重新登陆'}))
    tutor_status = request.POST.get('tutor_status')
    tutor_name = request.POST.get('tutor_name')
    tutor = TutorInfo.objects.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)).first()

    if not tutor:
        return HttpResponse(json.dumps({'code': 1, 'msg': 'tutor does not exits'}))

    if int(tutor_status) == 0:  # 上岗不隐藏

        tutor.hide = TutorInfo.DISPLAY
        tutor.working = TutorInfo.WORKING
        tutor.status = TutorInfo.ACTIVE
    elif int(tutor_status) == 1:  # 上岗隐藏

        tutor.hide = TutorInfo.HIDDEN
        tutor.working = TutorInfo.WORKING
        tutor.status = TutorInfo.ACTIVE

    elif int(tutor_status) == 2:  # 下岗
        tutor.hide = TutorInfo.HIDDEN
        tutor.working = TutorInfo.UNWORK
        tutor.status = TutorInfo.ACTIVE

    elif int(tutor_status) == 3:  # 未激活

        tutor.status = TutorInfo.NOTACTIVE
        tutor.hide = TutorInfo.HIDDEN
        tutor.working = TutorInfo.UNWORK
    tutor.working_time = timezone.now()
    tutor.save()
    logger.debug(
        'change tutor status, tutor_user_id: {}, operate_user_id:{}, operate_user_name: {}, tutor_status: {}'.format(
            tutor.id, request.user.id, request.user.username, tutor_status))

    return HttpResponse(json.dumps({'code': 0, 'msg': 'success'}))


# @login_required
def get_tutor_status(request):

    tutor_name = request.GET.get('tutor_name')

    tutor = TutorInfo.objects.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)).first()

    if not tutor:
        return HttpResponse(json.dumps({'code': 1, 'msg': 'tutor does not exits'}))

    if tutor.status == TutorInfo.ACTIVE:
        if tutor.working == TutorInfo.WORKING:
            if tutor.hide == TutorInfo.HIDDEN:
                tutor_status = 1   # 仅老生可见
            else:
                tutor_status = 0   # 上岗
        else:
            tutor_status = 2      # 下岗
    else:
        tutor_status = 3   # 未激活

    tutor_grades = ScheduleTutorLevel.objects.filter(tutor_user=tutor).all()

    tutor_levels = {}

    for tutor_grade in tutor_grades:
        tutor_levels[tutor_grade.course_edition.edition_name] = tutor_grade.user_level.id

    data = {
        'tutor_status': tutor_status,
        'tutor_levels': tutor_levels
    }

    return HttpResponse(json.dumps({'code': 0, 'msg': 'success', 'data': data}))


# @login_required
def set_tutor_area(request):

    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'status': 2, 'message': '登陆信息过期，请重新登陆'}))
    tutor_name = request.POST.get('tutor_name')
    local_area_status = request.POST.get('local_area_status')

    tutor = TutorInfo.objects.filter(Q(username=tutor_name) | Q(email=tutor_name) | Q(phone=tutor_name)).first()

    if not tutor:
        return HttpResponse(json.dumps({'code': 1, 'msg': 'tutor does not exits'}))

    tutor.local_area = local_area_status
    tutor.save()
    logger.debug(
        'change tutor area, tutor_user_id: {}, operate_user_id:{}, operate_user_name: {}, tutor_local_area: {}'.format(
            tutor.id, request.user.id, request.user.username, local_area_status))
    return HttpResponse(json.dumps({'code': 0, 'msg': 'success'}))


class FilterTeacherViewSet(viewsets.ModelViewSet):

    serializer_class = TeacherListSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = TeacherFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    pagination_class = TeacherPagination
    ordering_fields = ('total_number_of_class', 'student_sum', 'student_num', 'first_course_sum', 'first_course_recharge_sum')

    def get_queryset(self):

        month_ago = timezone.now() - timedelta(days=30)  # 30天之内的学生

        queryset = TutorInfo.objects.all().extra(
            select={
                'student_sum': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                where cvi.tutor_user_id=user_tutor_info.id and cvi.status in ({}, {}, {})'''.format(VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED, VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'student_num': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                where cvi.tutor_user_id=user_tutor_info.id and cvi.start_time>='{}' and cvi.status in ({}, {}, {})'''.format(utils.datetime_str(month_ago), VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED, VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'first_course_sum': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                where cvi.tutor_user_id=user_tutor_info.id and svm.first_course={} and cvi.status={}'''.format(VirtualclassInfo.FIRST_COURSE, VirtualclassInfo.FINISH_NOMAL)
            }
        )
        queryset = queryset.prefetch_related('tutor_course').prefetch_related('tutor_class_type').prefetch_related('tutor_course__course').prefetch_related('tutor_course__course__course_edition').distinct()
        return queryset

    @action(methods=['get'], detail=True)
    def timetable(self, request, pk):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        timetable_url = 'http://' + settings.JAVA_DOMAIN + settings.TUTOR_TIME_TABLE.format(tutor_user_id=pk, start_time=start_time, end_time=end_time)

        result = utils.fetch_get_api(timetable_url)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='获取教师列表失败,{}'.format(result.get('message', '')), status=status.HTTP_200_OK)
        return JsonResponse(code=0, msg='success', data=result.get('data'), status=status.HTTP_200_OK)


class TeacherMatchViewSet(viewsets.ModelViewSet):

    serializer_class = MatchTutorInfoSerializer
    pagination_class = TeacherPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = TeacherFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):

        month_ago = timezone.now() - timedelta(days=30)  # 30天之内的学生

        query_start_time = self.request.query_params.get('start_time')

        UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

        start_time = datetime.strptime(query_start_time, UTC_FORMAT)

        before_time = start_time - timedelta(minutes=30)
        after_time = start_time + timedelta(minutes=30)

        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        before_time = before_time.strftime("%Y-%m-%d %H:%M:%S")
        after_time = after_time.strftime("%Y-%m-%d %H:%M:%S")

        start_time_result = """select IFNULL(count(*), 0) from schedule_tutor_timetable stt where stt.start_time='{}' and stt.tutor_user_id=user_tutor_info.id and stt.status={}""".format(start_time, TutorTimetable.PUBLISHED)
        before_time_result = """select IFNULL(count(*), 0) from schedule_tutor_timetable stt where stt.start_time='{}' and stt.tutor_user_id=user_tutor_info.id and stt.status in ({}, {})""".format(before_time, TutorTimetable.SUCCESS_APPOINTMENT, TutorTimetable.OCCUPATION)
        after_time_result = """select IFNULL(count(*), 0) from schedule_tutor_timetable stt where stt.start_time='{}' and stt.tutor_user_id=user_tutor_info.id and stt.status in ({}, {})""".format(after_time, TutorTimetable.SUCCESS_APPOINTMENT, TutorTimetable.OCCUPATION)

        queryset = TutorInfo.objects.all().extra(
            select={
                'student_count': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                                    left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                                    where cvi.tutor_user_id=user_tutor_info.id and cvi.start_time>='{}' and cvi.status in ({}, {}, {})'''.format(
                    utils.datetime_str(month_ago), VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED,
                    VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'start_time_result': start_time_result
            }
        ).extra(
            select={
                'before_time_result': before_time_result
            }
        ).extra(
            select={
                'after_time_result': after_time_result
            }
        )

        student_user_id = self.request.query_params.get('student_user_id')
        student_user = UserStudentInfo.objects.get(id=student_user_id)
        queryset = queryset.filter(tutor_course__course_id=student_user.course.id)

        tutor_type = self.request.query_params.get('tutor_type', '')

        if tutor_type == 'often_tutor':

            tutor_ids = VirtualclassInfo.objects.filter(status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED), virtual_class_member__student_user_id=student_user_id).values_list('tutor_user_id').distinct()

            queryset = queryset.filter(id__in=tutor_ids)

        elif tutor_type == 'able_tutor':

            tutor_ids = VirtualclassInfo.objects.filter(status=VirtualclassInfo.FINISH_NOMAL, virtual_class_member__student_user_id=student_user_id).values_list('tutor_user_id')

            queryset = queryset.filter(~Q(id__in=tutor_ids))

        queryset = queryset.extra(
            where=['({})>0 and ({})=0 and ({})=0'.format(start_time_result, before_time_result, after_time_result)]
        )
        return queryset

    @action(methods=['get'], detail=True)
    def ceshi(self, request, pk):

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)
