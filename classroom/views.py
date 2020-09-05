import time
import logging
from decimal import Decimal
from django.contrib.auth.decorators import permission_required
from classroom.models import VirtualclassInfo, VirtualclassComment, ClassInfo, \
    get_video_service_provider, VirtualclassType, ClassType, VirtualclassException
from classroom import utils as classroom_utils, classroom_controller, baijiayun
from django.utils import timezone
from django.shortcuts import render, redirect
from datetime import timedelta
from utils import utils
from classroom.serializers import CommentSerializer
from rest_framework import viewsets, exceptions, status
from classroom.serializers import VritualclassInfoSerializer, SmallClassVirtualclassSerializer, \
    SmallClassVirtualclassInfoSerializer, ScheduleVirtualclassMemberSerializer, NewScheduleVirtualclassMemberSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from utils.pagination import LargeResultsSetPagination
from utils.viewset_base import JsonResponse
from classroom.filters import CommentFilter
from course.models import CourseInfo
from classroom.filters import VirtualclassInfoBackend, VirtualclassInfoFilter
from users.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.decorators import action
from finance.models import BalanceChange, AccountBalance, ClasstypePrice
from common.models import ExchangeRate
from django.core.exceptions import ObjectDoesNotExist
from course.models import CourseLesson
from django.utils.translation import ugettext as _
from django.conf import settings
import requests
from utils.utils import fetch_put_api
from manage.models import UserInfo
from rest_framework.response import Response
from course.serializers import CourseLessonSerializer
from tutor.models import TutorInfo
from scheduler.models import ScheduleVirtualclassMember
logger = logging.getLogger('pplingo.ng_webapp.classroom')


@permission_required('virtualclass.can_monitor_virtualclass')
def list_class(request):
    t_now = timezone.now()
    t_end = t_now + timedelta(minutes=5)
    t_start = t_now - timedelta(minutes=55)

    t_3_days = t_now + timedelta(days=3)

    virtual_classes = VirtualclassInfo.objects.filter(
        status__in=(VirtualclassInfo.STARTED, VirtualclassInfo.NOT_START),
        start_time__gte=t_start, start_time__lt=t_end)

    class_in_3_days = VirtualclassInfo.objects.filter(
        status=VirtualclassInfo.NOT_START,
        start_time__gte=t_end,
        start_time__lt=t_3_days).order_by('start_time')

    return render(request,
                  'man/virtualclass/list.html',
                  {'virtual_classes': virtual_classes,
                   'class_in_3_days': class_in_3_days})


@permission_required('virtualclass.can_monitor_virtualclass')
def convert_list(request):

    t_now = timezone.now()
    t_end = t_now + timedelta(days=1)
    t_start = t_now - timedelta(minutes=55)

    t_3_days = t_now + timedelta(days=3)

    virtual_classes = VirtualclassInfo.objects.filter(
        status__in=(VirtualclassInfo.STARTED, VirtualclassInfo.NOT_START),
        start_time__gte=t_start,
        start_time__lt=t_end)

    class_in_3_days = VirtualclassInfo.objects.filter(
        status=VirtualclassInfo.NOT_START,
        start_time__gte=t_end,
        start_time__lt=t_3_days).order_by('start_time')

    return render(request,
                  'man/virtualclass/convert_list.html',
                  {'virtual_classes': virtual_classes,
                   'class_in_3_days': class_in_3_days})


@permission_required('virtualclass.can_monitor_virtualclass')
def revert(request):
    """
    在巡课位置,拓课切换声网,
    在声网切拓课的时候,要判断是否已经有了tk_class_id, 如果已经有了, 直接切换, 如果没有创建教室,update VC.
    :param request:
    :return:
    """
    vc_id = request.GET.get('vc_id')
    vc = VirtualclassInfo.objects.get(id=vc_id)
    is_smallclass = classroom_utils.is_small_class(vc_type=vc.class_type_id)
    if vc.virtualclass_type_id == classroom_utils.TK_CLASS_ROOM:
        if not is_smallclass:
            vc.virtualclass_type_id = classroom_utils.AGORA_CLASS_ROOM
    else:
        if vc.tk_class_id:
            vc.virtualclass_type_id = classroom_utils.TK_CLASS_ROOM
        else:
            roomname = vc.student_user.parent_user.username
            chairmanpwd = 'lingoace'
            # 设置虚拟课堂开始上课时间
            starttime = time.time()  # 生成appointment 的时候创建虚拟教室
            # 设置虚拟课堂结束时间
            end_time = time.mktime(vc.start_time.timetuple())

            endtime = end_time + 1 * 24 * 3600  # 教室保留1天自动消除.
            assistantpwd = 'assistant'
            patrolpwd = 'patrol'
            confuserpwd = 'student'
            autoopenav = 1
            roomtype = classroom_utils.get_tk_roomtype(vc_type=vc.class_type_id)

            classid = classroom_controller.create_tk_room(chairmanpwd, roomname, starttime,
                                     endtime, assistantpwd, patrolpwd,
                                     confuserpwd, roomtype)
            vc.tk_class_id = classid
            vc.virtualclass_type_id = classroom_utils.TK_CLASS_ROOM
    vc.save()
    return redirect('/man')


@permission_required('virtualclass.can_monitor_virtualclass')
def monitor_tk(request):
    usertype = 4
    vc_id = request.GET.get('vc_id')
    vc = VirtualclassInfo.objects.get(id=vc_id)
    entrytkpath = classroom_controller.entry_class_path(serial=vc.tk_class_id, username=request.user.username, usertype=usertype)

    return redirect(entrytkpath)


@permission_required('virtualclass.can_monitor_virtualclass')
def monitor(request):

    vc_id = request.GET.get('vc_id')

    no_class = _('You do not have any appointment within 5 minutes')
    wrong_data = _('user data is not correct')

    role = 'monitor'

    tokens = []
    logger.debug('user role is {0}'.format(role))

    try:
        virtual_class = VirtualclassInfo.objects.get(id=vc_id)
    except VirtualclassInfo.DoesNotExist:
        return render(request, 'man/virtualclass/list.html', {'notification': no_class})

    logger.debug('virtual class is {0}'.format(virtual_class))

    token_id = virtual_class.get_token_id(request.user.username, role)

    logger.debug('token id is {0}'.format(token_id))

    api_key = virtual_class.api_key
    session_id = virtual_class.session_id

    student = virtual_class.student_user
    if not student:
        return render(request, 'man/virtualclass/list.html', {'notification': wrong_data})
    try:
        lesson = student.lesson
    except CourseLesson.DoesNotExist:
        return render(request, 'man/virtualclass/list.html', {'notification': wrong_data})
    logger.debug('lesson name is %s' % lesson.lesson_name)

    tutor = virtual_class.tutor_user

    request.session['role'] = role

    provider = get_video_service_provider(virtual_class)

    target = 'man/virtualclass/monitor.html'
    return render(request, target, { 'virtual_class': virtual_class,
                                                       'api_key': api_key,
                                                       'session_id': session_id,
                                                       'token': token_id,
                                                       'student': student,
                                                       'tutor': tutor,
                                                       'course_lesson': lesson,
                                                       'role': role,
                                                       'username': request.user.username,
                                                       'userid': request.user.id,
                                                       })


class ClassroomViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    # serializer_class = VritualclassInfoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, VirtualclassInfoBackend, filters.OrderingFilter)
    filter_class = VirtualclassInfoFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('start_time',)

    def permission_denied(self, request, message=None):
        '''
        没有权限时的返回值
        :param request:
        :param message:
        :return:
        '''
        if not message:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message)

    def get_serializer_class(self):
        if self.action == 'timetable_format_time':
            return SmallClassVirtualclassSerializer
        elif self.action == 'timetable_format_class':
            return SmallClassVirtualclassSerializer
        else:
            return VritualclassInfoSerializer

    def get_serializer_context(self):
        if self.action == 'list':
            users = UserInfo.objects.all().only('id', 'username', 'realname')
            result = {}
            for user in users:
                result[user.id] = user
            return {
                'request': self.request,
                'format': self.format_kwarg,
                'appoint_status': self.request.query_params.get('appoint_status'),
                'user_infos': result
            }

        return {
            'request': self.request,
            'format': self.format_kwarg,
            'appoint_status': self.request.query_params.get('appoint_status')
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        # kwargs['context'] = self.get_serializer_context()  # 获取参数集合, 封装参数到kwargs的context中
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        if self.action == 'timetable_format_time':
            queryset = VirtualclassInfo.objects.filter(~Q(status=VirtualclassInfo.CANCELED),
                                                       ~Q(class_type_id=ClassType.ONE2ONE)).all()
            return queryset
        elif self.action == 'timetable_format_class':
            queryset = VirtualclassInfo.objects.filter(~Q(status=VirtualclassInfo.CANCELED),
                                                       ~Q(class_type_id=ClassType.ONE2ONE)).all()
            return queryset
        queryset = VirtualclassInfo.objects.filter(~Q(status=VirtualclassInfo.CANCELED)).all()
        queryset = queryset.select_related('virtualclass_type', 'class_type', 'tutor_user')\
            .only('id', 'start_time', 'lesson_id', 'actual_start_time', 'actual_end_time', 'status', 'first_course', 'tk_class_id', 'bj_class_id', 'reason', 'remark', 'create_time', 'absent_tutor_user_id', 'student_user_id',
                  'tutor_user__id', 'tutor_user__username', 'tutor_user__total_number_of_class', 'tutor_user__real_name', 'tutor_user__identity_name',
                  'virtualclass_type__name', 'class_type__name')
        return queryset

    def add_course_lesson(self, data):

        course_lesson_ids = []
        for d in data:
            course_lesson_ids.append(d.get('lesson_id'))
        lessons = CourseLesson.objects.filter(id__in=course_lesson_ids).select_related('course').select_related('course__course_edition').all()
        lesson_serializers = CourseLessonSerializer(lessons, many=True)
        lesson_dict = {}
        for lesson in lesson_serializers.data:
            lesson_dict[lesson.get('id')] = lesson
        for d in data:
            d['lesson'] = lesson_dict.get(d.get('lesson_id'))
        return data

    def add_absent_tutor_user(self, data):
        for d in data:
            absent_tutor_user_id = d.get('absent_tutor_user_id')
            if absent_tutor_user_id:
                absent_tutor = TutorInfo.objects.filter(id=absent_tutor_user_id).only('real_name').first()
                d['absent_tutor_user'] = absent_tutor.real_name
            else:
                d['absent_tutor_user'] = None
        return data

    def user_list(self):
        users = UserInfo.objects.all().only('id', 'username', 'realname')
        result = {}
        for user in users:
            result[user.id] = user
        return result

    def add_schedule_virtualclass_member(self, data):

        user_infos = self.user_list()
        for d in data:
            virtual_class_id = d.get('id')
            virtualclass_members = ScheduleVirtualclassMember.objects.filter(virtual_class_id=virtual_class_id, class_type_id__in=(1,2)).select_related('student_user').select_related('student_user__parent_user').all().only(
                'enter_time', 'leave_time', 'student_user_id', 'first_course', 'class_type_id',
                'student_user__real_name',
                'student_user__parent_user__username', 'student_user__parent_user__adviser_user_id',
                'student_user__parent_user__xg_user_id', 'student_user__parent_user__nationality'
            )
            member_serializer = NewScheduleVirtualclassMemberSerializer(virtualclass_members, many=True, context={'user_infos': user_infos})
            d['virtual_class_member'] = member_serializer.data
        return data

    def add_examine_status(self, data):
        virtualclass_ids = []
        for d in data:
            virtual_class_id = d.get('id')
            virtualclass_ids.append(virtual_class_id)
        virtualclass_exceptions = VirtualclassException.objects.filter(virtual_class_id__in=virtualclass_ids).all().values('virtual_class_id')
        for d in data:
            virtual_class_id = d.get('id')
            if virtual_class_id in virtualclass_exceptions:
                d['examine_status'] = '已审核'
            else:
                d['examine_status'] = '未审核'
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_course_lesson(serializer.data)
            # data = self.add_absent_tutor_user(data)
            data = self.add_schedule_virtualclass_member(data)
            data = self.add_examine_status(data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def details(self, request, pk):
        virtualclass = VirtualclassInfo.objects.filter(id=pk).first()
        serializer = self.get_serializer(virtualclass)
        return JsonResponse(code=0, msg='success', data=serializer.data, status=status.HTTP_200_OK)

    # 课堂转换
    @action(methods=['get'], detail=True)
    def revert(self, request, pk):

        # vc = self.get_object()
        vc = VirtualclassInfo.objects.filter(id=pk).first()
        if vc.status in (VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL):
            return JsonResponse(code=1, msg='已结束授课', status=status.HTTP_200_OK)
        if vc.virtualclass_type_id == classroom_utils.TK_CLASS_ROOM:
            vc.virtualclass_type_id = classroom_utils.BAIJIAYUN_ROOM
        else:
            vc.virtualclass_type_id = classroom_utils.TK_CLASS_ROOM
        vc.save()

        try:
            user = request.session.get('user')
            logger.debug('revert virtualclass type , user={}, virtualclass_id={}'.format(user.get('id'), pk))
        except Exception as e:
            logger.debug('revert virtualclass type fail, error='.format(e))

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 批量课堂转换
    @action(methods=['post'], detail=False)
    def revert_list(self, request):
        try:
            virtual_class_ids = request.data.get('virtual_class_ids')
            virtual_class_type = int(request.data.get('virtual_class_type'))
        except:
            return JsonResponse(code=1, msg='参数错误', status=status.HTTP_200_OK)

        VirtualclassInfo.objects.filter(id__in=virtual_class_ids,
                                        status__in=(VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED)).update(
            virtualclass_type_id=virtual_class_type)

        try:
            user = request.session.get('user')
            logger.debug('revert virtualclass type , user={}, virtualclass_ids={}, virtual_class_type={}'.format(user.get('id'), ','.join(virtual_class_ids), virtual_class_type))
        except Exception as e:
            logger.debug('revert virtualclass type fail, error='.format(e))

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 旁听
    @action(methods=['get'], detail=True)
    def monitor(self, request, pk):
        # virtual_class = self.get_object()
        virtual_class = VirtualclassInfo.objects.filter(id=pk).first()
        user = request.session.get('user')

        if not virtual_class:
            return JsonResponse(code=1, msg='未找到课堂', status=status.HTTP_200_OK)

        if virtual_class.virtualclass_type_id == classroom_utils.BAIJIAYUN_ROOM:
            bj_class_id = virtual_class.bj_class_id
            if not bj_class_id:
                return JsonResponse(code=1, msg='未找到百家云课堂', status=status.HTTP_200_OK)
            bj_class_id = virtual_class.bj_class_id.split(',')[0]
            entrytkpath = baijiayun.monitor_baijiayun(bj_class_id, user.get('id'), user.get('username'))
            # entrytkpath = baijiayun.monitor_baijiayun(virtual_class.bj_class_id, 123456, student_user.real_name)

            data = {
                'virtualclass_type': virtual_class.virtualclass_type.name,
                'entrytkpath': entrytkpath
            }
            logger.debug('baijiayun entrytkpath {}'.format(entrytkpath))
            return JsonResponse(data=data, code=0, msg='success', status=status.HTTP_200_OK)
        elif virtual_class.virtualclass_type_id == classroom_utils.TK_CLASS_ROOM:
            if not virtual_class.tk_class_id:
                return JsonResponse(code=1, msg='未找到拓课教室', status=status.HTTP_200_OK)
            usertype = 1  # 旁听以助教身份进入
            entrytkpath = classroom_controller.entry_class_path(serial=virtual_class.tk_class_id, username=user.get('username'), usertype=usertype)
            data = {
                'virtualclass_type': virtual_class.virtualclass_type.name,
                'entrytkpath': entrytkpath
            }
            return JsonResponse(data=data, code=0, msg='success', status=status.HTTP_200_OK)
        else:
            return JsonResponse(code=1, msg='virtualclass数据错误', status=status.HTTP_200_OK)

    # 课堂回放
    @action(methods=['get'], detail=True)
    def course_playback(self, request, pk):
        # vc = self.get_object()
        vc = VirtualclassInfo.objects.filter(id=pk).first()
        if vc.virtualclass_type_id == VirtualclassType.BAIJIAYUN:
            if not vc.bj_class_id:
                return JsonResponse(code=1, msg='未找到教室', status=status.HTTP_200_OK)
            bj_class_id = vc.bj_class_id.split(',')[0]
            session_mp4_record = baijiayun.playback(bj_class_id)
        else:
            if not vc.tk_class_id:
                return JsonResponse(code=1, msg='未找到教室', status=status.HTTP_200_OK)
            session_mp4_record = classroom_controller.seeze_tk_record(vc.tk_class_id)
        return JsonResponse(code=0, msg='success', data={'mp4_url': session_mp4_record, 'virtualclass_type': vc.class_type_id}, status=status.HTTP_200_OK)

    # 老师评语
    @action(methods=['get'], detail=True)
    def comment(self, request, pk):
        target = request.query_params.get('target')
        if not target or target not in ('Student', 'Tutor'):
            return JsonResponse(code=1, msg='参数错误', status=status.HTTP_200_OK)
        comments = VirtualclassComment.objects.filter(virtual_class_id=pk)
        result = {}
        comment_result = {}
        # 老师反馈
        if target == 'Student':
            valuations = comments.filter(role=VirtualclassComment.TEACHER)
            for valuation in valuations:
                student_name = valuation.student_user.real_name   # 被评论者姓名
                if student_name not in result.keys():
                    result[student_name] = {}
                result[student_name]['rating_le'] = valuation.rating_le
                result[student_name]['rating_id'] = valuation.rating_id
                result[student_name]['rating_pk'] = valuation.rating_pk
                if student_name not in comment_result.keys():
                    comment_result[student_name] = {}
                comment_result[student_name]['comment'] = valuation.comment_zh
                comment_result[student_name]['commentor'] = valuation.tutor_user.__str__()

        elif target == 'Tutor':
        # 学生反馈  以学生姓名做key
            valuations = comments.filter(role=VirtualclassComment.STUDENT)
            for valuation in valuations:
                teacher_name = valuation.tutor_user.__str__()  # 老师姓名
                student_name = valuation.student_user.real_name   # 学生姓名
                if student_name not in result.keys():
                    result[student_name] = {}
                result[student_name]['rating_le'] = valuation.rating_le
                result[student_name]['rating_id'] = valuation.rating_id
                result[student_name]['rating_pk'] = valuation.rating_pk
                result[student_name]['teacher'] = teacher_name
                if student_name not in comment_result.keys():
                    comment_result[student_name] = {}
                comment_result[student_name]['comment'] = valuation.comment_zh
                comment_result[student_name]['teacher'] = teacher_name
        data = {
            'comment': comment_result,
            'valuation': result
        }
        return JsonResponse(code=0, msg='success', data=data, status=status.HTTP_200_OK)

    # 异常审核结果
    @action(methods=['get'], detail=True)
    def virtualclass_exception(self, request, pk):
        vc = VirtualclassInfo.objects.filter(id=pk).first()
        if not vc:
            return JsonResponse(code=1, msg='数据错误, 未查询到virtualclass', status=status.HTTP_200_OK)
        now_time = timezone.now()
        if (vc.start_time > now_time - timedelta(hours=2) and vc.status == VirtualclassInfo.NOT_START) \
                or vc.status == VirtualclassInfo.STARTED:
            return JsonResponse(code=1, msg='课堂未结束，不能审核', status=status.HTTP_200_OK)

        if vc.reason is not None and vc.reason == VirtualclassInfo.NORMAL and vc.status == VirtualclassInfo.FINISH_NOMAL:
            return JsonResponse(code=1, msg='该课堂正常结束', status=status.HTTP_200_OK)

        vc_exception_result = VirtualclassException.objects.filter(virtual_class_id=pk).first()

        if not vc_exception_result:
            data = dict(
                tag=0,  # 未审核
                submitter=vc.tutor_user.__str__(),
                submit_time=utils.datetime_to_str(vc.update_time) if vc.update_time else None,
                end_reason=vc.reason if vc.reason else 21,
                end_reason_description=vc.remark
            )
            return JsonResponse(code=0, msg='success', data=data, status=status.HTTP_200_OK)

        student_amount = 0
        teacher_amount = 0
        account_balance_change = BalanceChange.objects.filter(
            reason__in=(BalanceChange.ABSENCE_PENALTY,   # 学生缺席罚金
                        BalanceChange.NO_SHOW_COMPENSATION,   # 导师不出席对学生的补偿
                        BalanceChange.ABSENCE_COMPENSATION,   # 学生缺席老师奖励
                        BalanceChange.NO_SHOW_PENALTY,    #  老师缺席罚金
                        ), reference=vc.id).all()
        for account in account_balance_change:
            if account.reason == BalanceChange.ABSENCE_PENALTY:
                student_amount = account.amount
            elif account.reason == BalanceChange.NO_SHOW_COMPENSATION:
                student_amount = account.amount
            elif account.reason == BalanceChange.ABSENCE_COMPENSATION:
                teacher_amount = account.amount
            elif account.reason == BalanceChange.NO_SHOW_PENALTY:
                teacher_amount = account.amount

        exchange = ExchangeRate.objects.filter(currency='CNY', valid_start__lt=now_time, valid_end__gte=now_time).first()

        data = dict(
            tag=1,  # 已审核
            submitter=vc.tutor_user.__str__(),
            submit_time=utils.datetime_to_str(vc.update_time) if vc.update_time else None,
            end_reason=vc.reason,
            end_reason_description=vc.remark,
            check_result=vc.get_reason_display(),
            check_description=vc_exception_result.description if vc_exception_result else '系统审核',
            check_code=vc_exception_result.result if vc_exception_result else vc.reason,
            student_amount=abs(student_amount)*exchange.rate,
            teacher_amount=abs(teacher_amount)*exchange.rate,
            check_user=vc_exception_result.cms_user.realname if vc_exception_result else '系统审核',
            check_time=utils.datetime_to_str(vc.update_time)
        )

        return JsonResponse(code=0, msg='success', data=data, status=status.HTTP_200_OK)

    # 异常审核
    @action(methods=['put'], detail=True)
    def check_exception(self, request, pk):
        try:
            result = int(request.data.get('result'))
            student_amount = Decimal(request.data.get('student_amount', 0))
            teacher_amount = Decimal(request.data.get('teacher_amount', 0))
            description = request.data.get('description', None)
            if student_amount > 200 or student_amount < 0:
                raise ArithmeticError('参数超出范围')
            if teacher_amount > 200 or teacher_amount < 0:
                raise ArithmeticError('参数超出范围')
        except Exception as e:
            logger.error(e)
            return JsonResponse(code=1, msg='参数错误', status=status.HTTP_200_OK)
        try:
            vc = VirtualclassInfo.objects.get(id=pk)
            if vc.reason == VirtualclassInfo.NORMAL and vc.status == VirtualclassInfo.FINISH_NOMAL:
                return JsonResponse(code=1, msg='该课堂正常结束，不能审核', status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse(code=1, msg='该课堂不存在', status=status.HTTP_200_OK)
        user = request.session.get('user')
        logger.debug('check_exception, operator:{}, result:{}, student_amount:{}, teacher_amount:{}, description:{}, virtual_class_id:{}'.format(
            user.get('id'), result, student_amount, teacher_amount, description, pk))
        now_time = timezone.now()

        members = vc.virtual_class_member.all()
        students = [member.student_user for member in members]
        teacher = vc.tutor_user
        vc_exception = VirtualclassException.objects.filter(virtual_class_id=vc.id).first()
        if vc_exception:
            return JsonResponse(code=1, msg='该条数据已审核，请勿重复审核', status=status.HTTP_200_OK)
        account_balance_change = BalanceChange.objects.filter(
            reason__in=(BalanceChange.ABSENCE_PENALTY,  # 学生缺席罚金
                        BalanceChange.NO_SHOW_COMPENSATION,  # 导师不出席对学生的补偿
                        BalanceChange.ABSENCE_COMPENSATION,  # 学生缺席老师奖励
                        BalanceChange.NO_SHOW_PENALTY,  # 老师缺席罚金
                        ), reference=vc.id).all()
        if len(account_balance_change) > 1:
            return JsonResponse(code=1, msg='该条数据已审核，请勿重复审核', status=status.HTTP_200_OK)
        vc_exception = VirtualclassException()
        vc_exception.result = result
        vc_exception.description = description
        vc_exception.cms_user_id = request.session.get('user').get('id')
        vc_exception.virtual_class_id = vc.id

        exchange = ExchangeRate.objects.filter(currency='CNY', valid_start__lt=now_time,
                                               valid_end__gte=now_time).first()

        account_class = AccountBalance.NORMAL_ACCOUNT
        class_type_price = ClasstypePrice.objects.filter(class_type_id=vc.class_type_id, course_edition_id=vc.lesson.course.course_edition.id).first()
        if class_type_price:
            account_class = class_type_price.account_class
        if result == VirtualclassException.STUDENT_ABSENCE:  # 学生缺席
            '''学生缺席，对老师进行补偿，对学生进行扣款'''
            vc.reason = VirtualclassInfo.STUDENT_ABSENCE
            vc.status = VirtualclassInfo.FINISH_ABNOMAL
            vc.save()
            if student_amount:
                student_amount = 0 - (student_amount/exchange.rate)
                self.absence_penalty(vc, students, student_amount, account_class)
            else:
                self.add_student_fbc(vc, students, BalanceChange.ABSENCE_PENALTY)

            teacher_amount = teacher_amount / exchange.rate
            BalanceChange.save_balance_change(BalanceChange.TEACHER, teacher.id, vc.id,
                                              BalanceChange.ABSENCE_COMPENSATION, teacher_amount)

        elif result == VirtualclassException.TEACHER_ABSENCE:  # 老师缺席
            '''老师缺席，对学生进行补偿，对老师进行扣款'''
            vc.reason = VirtualclassInfo.TUTOR_ABSENCE
            vc.status = VirtualclassInfo.FINISH_ABNOMAL
            vc.save()
            if student_amount:
                student_amount = student_amount / exchange.rate
                self.compensation_student(vc, students, student_amount, account_class)
            else:
                self.add_student_fbc(vc, students, BalanceChange.NO_SHOW_COMPENSATION)

            teacher_amount = 0 - (teacher_amount/exchange.rate)
            BalanceChange.save_balance_change(BalanceChange.TEACHER, teacher.id, vc.id,
                                              BalanceChange.NO_SHOW_PENALTY, teacher_amount)

        elif result == VirtualclassException.TEACHER_AND_STUDENT_ABSENCE:  # 老师学生都缺席
            '''老师学生都缺席，对学生老师进行扣款'''
            vc.status = VirtualclassInfo.FINISH_ABNOMAL
            vc.reason = VirtualclassInfo.CLASS_NOONE
            vc.save()
            teacher_amount = 0 - (teacher_amount / exchange.rate)
            BalanceChange.save_balance_change(BalanceChange.TEACHER, teacher.id, vc.id,
                                              BalanceChange.NO_SHOW_PENALTY, teacher_amount)
            if student_amount:
                student_amount = 0 - (student_amount/exchange.rate)
                self.absence_penalty(vc, students, student_amount, account_class)
            else:
                self.add_student_fbc(vc, students, BalanceChange.ABSENCE_PENALTY)
        vc_exception.save()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)


    # 学生账户修改是0时
    def add_student_fbc(self, vc, students, reason):
        for student in students:
            parent_user = student.parent_user
            BalanceChange.save_balance_change(BalanceChange.CHILDREN,
                                              student.id,
                                              vc.id,
                                              reason,
                                              0,
                                              parent_user_id=parent_user.id,
                                              adviser_user_id=parent_user.adviser_user_id,
                                              xg_user_id=parent_user.xg_user_id,
                                              balance_id=None)

    # 查询出需要修改的用户账户
    def select_account(self, parent_user, account_class):

        account_balance = AccountBalance.objects.filter(balance__gt=0, account_class=account_class, parent_user_id=parent_user.id, state=AccountBalance.NOT_DELETE, status=0)

        if account_class == AccountBalance.PRIVATE_ACCOUNT:
            account_balance = account_balance.order_by('-type', 'id')
        else:
            account_balance = account_balance.order_by('type', 'id')

        account_balance = account_balance.first()
        if account_balance:
            return account_balance
        return None

    # 创建一个运营账户
    def create_account(self, parent_user, type, account_class):
        account_balance = AccountBalance()
        account_balance.parent_user_id = parent_user.id
        account_balance.type = type
        account_balance.account_class = account_class
        account_balance.rate = 0
        account_balance.balance = 0
        account_balance.status = 0
        account_balance.save()
        return account_balance

    # 补偿学生
    def compensation_student(self, vc, students, student_amount, account_class):

        for student in students:
            parent_user = student.parent_user
            account_balance = self.create_account(parent_user, AccountBalance.ACTIVITY_AMOUNT, account_class)
            BalanceChange.save_balance_change(BalanceChange.CHILDREN,
                                              student.id,
                                              vc.id,
                                              BalanceChange.NO_SHOW_COMPENSATION,
                                              student_amount,
                                              parent_user_id=parent_user.id,
                                              adviser_user_id=parent_user.adviser_user_id,
                                              xg_user_id=parent_user.xg_user_id,
                                              balance_id=account_balance.id)
        return True

    # 学生罚款
    def absence_penalty(self, vc, students, student_amount, account_class):

        for student in students:
            parent_user = student.parent_user
            self.absence_student_account(vc, student, parent_user, student_amount, account_class)
        return True

    def absence_student_account(self, vc, student_user, parent_user, student_amount, account_class):
        '''循环扣学生课时'''

        while student_amount < 0:
            account_balance = self.select_account(parent_user, account_class)

            if not account_balance:

                account_balance = self.create_account(parent_user, AccountBalance.TOPUP_AMOUNT, account_class)
                self.save_balance_change(vc, student_user, parent_user, student_amount, BalanceChange.ABSENCE_PENALTY, account_balance)
                student_amount = 0
                continue

            if account_balance.balance >= abs(student_amount):

                self.save_balance_change(vc, student_user, parent_user, student_amount, BalanceChange.ABSENCE_PENALTY, account_balance)
                student_amount = 0
                continue

            elif account_balance.balance < abs(student_amount):
                student_amount = account_balance.balance + student_amount
                self.save_balance_change(vc, student_user, parent_user, 0-account_balance.balance, BalanceChange.ABSENCE_PENALTY, account_balance)

    def save_balance_change(self, vc, student_user, parent_user, student_amount, balance_reason, account_balance):

        BalanceChange.save_balance_change(BalanceChange.CHILDREN,
                                          student_user.id,
                                          vc.id,
                                          balance_reason,
                                          student_amount,
                                          parent_user_id=parent_user.id,
                                          adviser_user_id=parent_user.adviser_user_id,
                                          xg_user_id=parent_user.xg_user_id,
                                          balance_id=account_balance.id)

    # 发放课酬
    @action(methods=['put'], detail=True)
    def finish_virtualclass(self, request, pk):

        virtualclass_info = VirtualclassInfo.objects.get(id=pk)

        finish_virtualclass_info = settings.FINISH_VIRTUALCLASS.format(virtualclass_id=virtualclass_info.id, tutor_user_id=virtualclass_info.tutor_user_id)

        finish_virtualclass_url = 'http://' + settings.JAVA_DOMAIN + finish_virtualclass_info

        params = {
            'reason': 0,
            'remark': '数据修复'
        }
        user = request.session.get('user')

        result = fetch_put_api(finish_virtualclass_url, params, user_id=user.get('id'))

        if not result:
            return JsonResponse(code=1, msg='服务器错误', status=status.HTTP_200_OK)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg=result.get('message'), status=status.HTTP_200_OK)

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 小班课课表 时间格式显示
    @action(methods=['get'], detail=False)
    def timetable_format_time(self, request):
        queryset = self.filter_queryset(self.get_queryset()).select_related('tutor_user').select_related('class_field').select_related('lesson').select_related('lesson__course').select_related('lesson__course__course_edition')

        queryset = queryset.only('id', 'start_time', 'lesson_id',
                                 'tutor_user__id', 'tutor_user__username', 'tutor_user__total_number_of_class', 'tutor_user__real_name', 'tutor_user__identity_name',
                                 'class_field__id', 'class_field__class_no', 'class_field__class_name_zh', 'class_field__class_name', 'class_field__create_user_name')

        serializer = self.get_serializer(queryset, many=True)
        data = self.add_course_lesson(serializer.data)
        result = {}
        for s in data:
            start_time = s.pop('start_time')
            if start_time in result.keys():
                result[start_time].append(s)
            else:
                result[start_time] = []
                result[start_time].append(s)
        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)

    # 小班课课表  班级格式显示
    @action(methods=['get'], detail=False)
    def timetable_format_class(self, request):

        queryset = self.filter_queryset(self.get_queryset()).select_related('tutor_user').select_related('class_field').select_related('lesson').select_related('lesson__course').select_related('lesson__course__course_edition')

        queryset = queryset.only('id', 'start_time', 'lesson_id',
                                 'tutor_user__id', 'tutor_user__username', 'tutor_user__total_number_of_class', 'tutor_user__real_name', 'tutor_user__identity_name',
                                 'class_field__id', 'class_field__class_no', 'class_field__class_name_zh', 'class_field__class_name', 'class_field__create_user_name')

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        data = self.add_course_lesson(serializer.data)
        result = {}
        for s in data:
            class_info = s.get('class_field')
            class_id = class_info.pop('id')
            start_time = s.get('start_time')
            start_date = start_time.split(' ')[0]
            if class_id in result.keys():
                if start_date in result[class_id]:
                    result[class_id][start_date].append(s)
                else:
                    result[class_id][start_date] = []
                    result[class_id][start_date].append(s)
            else:
                result[class_id] = {}
                result[class_id][start_date] = []
                result[class_id][start_date].append(s)
        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)

    # 修改代课老师
    @action(methods=['post'], detail=False)
    def change_appointment_tutor(self, request):
        start_time = request.data.get('start_time')
        tutor_user_id = request.data.get('tutor_user_id')
        absent_tutor_user_id = request.data.get('absent_tutor_user_id')

        change_appointment_tutor_url = 'http://' + settings.JAVA_DOMAIN + settings.CHANGE_APPOINTMENTED_TUTOR.format(tutor_user_id=tutor_user_id, absent_tutor_user_id=absent_tutor_user_id, start_time=start_time)

        result = utils.fetch_post_api(change_appointment_tutor_url)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='{}'.format(result.get('message', '')), status=status.HTTP_200_OK)

        try:
            user = request.session.get('user')
            logger.debug('change appointment tutor , user={}, tutor_user_id={}, absent_tutor_user_id={}'.format(user.get('id'), tutor_user_id, change_appointment_tutor_url))
        except Exception as e:
            logger.debug('change appointment tutor fail, error='.format(e))

        return JsonResponse(code=0, msg='{}'.format(result.get('message', '')), status=status.HTTP_200_OK)


class SmallclassVirtualclassViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = SmallClassVirtualclassInfoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, VirtualclassInfoBackend, filters.OrderingFilter)
    filter_class = VirtualclassInfoFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('start_time',)

    def get_queryset(self):
        queryset = VirtualclassInfo.objects.filter(~Q(status=VirtualclassInfo.CANCELED),
                                                   ~Q(class_type_id=ClassType.ONE2ONE)).all()

        queryset = queryset.extra(
            select={
                'appointment_count': "select count(*) from classroom_virtualclass_info cvi where cvi.class_id=classroom_virtualclass_info.class_id and cvi.status in ({}, {}, {})".format(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.STARTED, VirtualclassInfo.NOT_START)
            }
        ).extra(
            select={
                'class_times': "select count(*) from classroom_virtualclass_info cvi where cvi.class_id=classroom_virtualclass_info.class_id and cvi.status in ({}, {}, {}) and cvi.start_time <= classroom_virtualclass_info.start_time".format(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.STARTED, VirtualclassInfo.NOT_START)
            }
        )
        queryset = queryset.select_related('tutor_user').select_related('class_field')
        return queryset

    # 修改班级名称
    @action(methods=['put'], detail=True)
    def edite_class_name(self, request, pk):
        class_info = self.get_object()
        class_name = request.data.get('class_name')
        class_info.class_name = class_name
        class_info.save()

        try:
            user = request.session.get('user')
            logger.debug('edite class name, user={}, class_id={}, class_name={}'.format(user.get('id'), class_info.id, class_name))
        except Exception as e:
            logger.debug('edite class name, fail, error='.format(e))

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

        # student.course_edition_id = course_edition_id
        # student.course_id = course_info.id
        # student.course_level = course_level
        # student.lesson_id = course_lesson.id
        # student.lesson_no = lesson_no
        # student.save()

        class_level_url = 'http://' + settings.JAVA_DOMAIN + settings.UPDATE_COURSE_LEVEL.format(class_id=pk, new_edition=course_edition, new_level=course_level, new_lesson_no=lesson_no)

        result = requests.put(class_level_url)

        result = result.json()

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='修改失败', status=status.HTTP_200_OK)

        try:
            user = request.session.get('user')
            logger.debug('edite class level, user={}, class_id={}, url={}'.format(user.get('id'), pk, class_level_url))
        except Exception as e:
            logger.debug('edite class level, fail, error='.format(e))

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    pagination_class = LargeResultsSetPagination
    serializer_class = CommentSerializer
    filter_class = CommentFilter

    def get_queryset(self):
        queryset = VirtualclassComment.objects.all()
        queryset = queryset.select_related('virtual_class').select_related('tutor_user').select_related('student_user').select_related('virtual_class__lesson').select_related('virtual_class__lesson__course').select_related('virtual_class__lesson__course__course_edition').select_related('student_user__parent_user')

        queryset = queryset.only('id', 'create_time', 'difficult_level', 'suggestion',
                                 'tutor_user__id', 'tutor_user__username', 'tutor_user__total_number_of_class', 'tutor_user__real_name', 'tutor_user__identity_name',
                                 'student_user__id', 'student_user__real_name',
                                 'student_user__parent_user__id', 'student_user__parent_user__username',
                                 'virtual_class__id', 'virtual_class__start_time',
                                 'virtual_class__lesson__id', 'virtual_class__lesson__lesson_no', 'virtual_class__lesson__unit_no',
                                 'virtual_class__lesson__course__id', 'virtual_class__lesson__course__course_name', 'virtual_class__lesson__course__course_level',
                                 'virtual_class__lesson__course__course_edition__id', 'virtual_class__lesson__course__course_edition__edition_name')
        return queryset

