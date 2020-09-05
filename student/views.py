from rest_framework import viewsets, exceptions
from utils.pagination import LargeResultsSetPagination
from student.filters import StudentManagerFilter, OldStudentManagerFilter, StudentFilterBackend
from common.models import CommonBussinessRule, CommonRuleFormula
from student.serializers import WarnStudentSerializer
from django.db.models import Sum, Q, Count
from student.serializers import StudentSerializer, OldStudentSerializer, ExtStudentUpdateSerializer, ExtStudentSerializer, \
    RemarkSerializer, RemarkListSerializer, StudentInfoSerializer, SmallClassStudentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from finance.models import BalanceChange
from student.models import UserStudentInfo, UserParentInfo, ExtStudent, StudentRemark, UserIp
from utils import utils
from utils.viewset_base import JsonResponse
from student.permissions import *
from users.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import json
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from classroom.models import VirtualclassInfo
from scheduler.models import ScheduleVirtualclassMember
from student.config import RECHARGED, REGISTER, APPOINTMENT, AUDITED
from finance.models import RechargeOrder, AccountBalance
from course.models import CourseAssessmentResult, CourseQuestionnaireResult, CourseEdition, \
    CourseInfo, CourseLesson
from django.conf import settings
from tutor.models import TutorInfo
from tutor.serializer import StudentAbleTutorSerializer
import requests
import logging
from manage.models import UserInfo, RoleInfo

logger = logging.getLogger('pplingo.ng_webapp.student')


class StudentManagerViewSet(viewsets.ModelViewSet):

    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, StudentFilterBackend)
    filter_class = StudentManagerFilter
    ordering_fields = ('create_time', 'parent_user__balance', 'smallclass_count', 'virtual_class_sum',
                       'recharge_sum', 'recharge_count', 'last_recharge_time', 'balance')

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

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.action == 'list':
            permissions.append(StudentListPermission())
        return permissions

    def get_serializer_class(self):

        if 'warn' in self.request.path:
            return WarnStudentSerializer
        else:
            return StudentSerializer

    def get_serializer_context(self):

        return {
            'source': self.request.query_params.get('source'),
            'student_status': self.request.query_params.get('student_status')
        }

    def get_warn_queryset(self):

        # 续费窗口用户（余额≤10）
        balance_sum = self.request.query_params.get('balance_sum')

        # 非活跃用户（累计充值≥10，近14天内没有上课且没有约课)
        active_balance_sum = self.request.query_params.get('active_balance_sum')  # 累计充值课时
        active_day = self.request.query_params.get('active_day')  # 近14天内没有上课且没有约课
        queryset = UserStudentInfo.objects.all()

        # 上课次数
        # virtual_class_sum = "select IFNULL(count(fbc.amount), 0) from finance_balance_change fbc where fbc.user_id=user_student_info.id and fbc.reason=1 group by fbc.user_id"
        virtual_class_sum = "select IFNULL(count(*), 0) from classroom_virtualclass_info cvi right join schedule_virtualclass_member svm on svm.virtual_class_id=cvi.id where svm.student_user_id=user_student_info.id and cvi.status={}".format(VirtualclassInfo.FINISH_NOMAL)
        # 累计充值课时
        recharge_sum = "select IFNULL(sum(fbc.amount), 0) from finance_balance_change fbc where fbc.user_id=user_student_info.parent_user_id and fbc.reason in(3, 16)"
        # 充值次数
        recharge_count = "select IFNULL(count(*), 0) from finance_recharge_order fro left join user_parent_info upi on upi.id=fro.parent_user_id where upi.id=user_student_info.parent_user_id and fro.status={}".format(RechargeOrder.PAID)
        # 最近充值时间
        last_recharge_time = "select IFNULL(max(fro.update_time), '') from finance_recharge_order fro left join user_parent_info upi on upi.id=fro.parent_user_id where upi.id=user_student_info.parent_user_id and fro.status={}".format(RechargeOrder.PAID)
        # 账户余额
        balance = "select sum(ab.balance) from accounts_balance ab where ab.parent_user_id=user_student_info.parent_user_id"
        queryset = queryset.extra(
            select={"virtual_class_sum": virtual_class_sum}
        ).extra(
            select={"recharge_sum": recharge_sum}
        ).extra(
            select={"recharge_count": recharge_count}
        ).extra(
            select={"last_recharge_time": last_recharge_time}
        ).extra(
            select={"balance": balance}
        )
        queryset = queryset.select_related('parent_user').only('id',
                                                               'real_name',
                                                               'create_time',
                                                               'first_course',
                                                               'parent_user_id',
                                                               'lesson_id',
                                                               'parent_user__adviser_user_id',
                                                               'parent_user__xg_user_id',
                                                               'parent_user__username',
                                                               'parent_user__email',
                                                               'parent_user__phone',
                                                               'parent_user__code',
                                                               'parent_user__referrer_user_id')
        if balance_sum:
            queryset = queryset.extra(
                where=['({}) <= {}'.format(balance, balance_sum)]
            )
            return queryset
        elif active_balance_sum:
            now_time = timezone.now()
            before_within_days = now_time - timedelta(days=int(active_day))
            # 最近几天内的上课次数
            within_days_virtualclass_sum = "select IFNULL(count(*), 0) from classroom_virtualclass_info cvi right join schedule_virtualclass_member svm on svm.virtual_class_id=cvi.id where svm.student_user_id=user_student_info.id and cvi.status={} and cvi.start_time >='{}'".format(VirtualclassInfo.FINISH_NOMAL, before_within_days.strftime('%Y-%m-%d %H:%M:%S'))
            queryset = queryset.extra(
                select={
                    'within_days_virtualclass_sum': within_days_virtualclass_sum
                }
            ).extra(
                where=['({})>={} and ({})=0'.format(recharge_sum, active_balance_sum, within_days_virtualclass_sum), "user_student_info.create_time<='{}'".format(before_within_days.strftime('%Y-%m-%d %H:%M:%S'))]
            )
            return queryset
        return queryset

    def get_queryset(self):

        # 判断是不是预警学生
        if 'warn' in self.request.path:
            return self.get_warn_queryset()

        queryset = UserStudentInfo.objects.all()
        recharge_sum = "select IFNULL(sum(fro.total_amount), 0) from finance_recharge_order fro where fro.parent_user_id=user_student_info.parent_user_id and fro.status=1"
        queryset = queryset.extra(
            select={"recharge_sum": recharge_sum}
        )
        student_status = self.request.query_params.get('student_status', None)

        queryset = queryset.select_related('parent_user').only('id',
                                                               'real_name',
                                                               'create_time',
                                                               'first_course',
                                                               'parent_user_id',
                                                               'lesson_id',
                                                               'lesson__course__course_name',
                                                               'parent_user__adviser_user_id',
                                                               'parent_user__xg_user_id',
                                                               'parent_user__username',
                                                               'parent_user__email',
                                                               'parent_user__phone',
                                                               'parent_user__code',
                                                               'parent_user__referrer_user_id')

        if student_status == RECHARGED:
            '''已充值： recharge_sum>0'''
            filter_sql = "({}) > 0".format(recharge_sum)
            queryset = queryset.extra(where=[filter_sql])
        elif student_status == REGISTER:
            '''已注册： 没有appointment'''
            user_ids = ScheduleVirtualclassMember.objects.filter(~Q(virtual_class__status__in=(VirtualclassInfo.CANCELED, VirtualclassInfo.FINISH_ABNOMAL)), ~Q(class_type_id=3)).values('student_user_id').distinct()
            queryset = queryset.filter(first_course=1).exclude(id__in=user_ids)
            return queryset
        elif student_status == AUDITED:
            '''已试听， reason=1 有数据'''
            queryset = queryset.filter(first_course=0)
        elif student_status == APPOINTMENT:
            '''已预约试听  first_course=1'''
            queryset = queryset.filter(virtual_class_member__virtual_class__status__in=(VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED), first_course=1, virtual_class_member__class_type_id__in=(1,2))
            return queryset.distinct()
        return queryset

    def add_course_info(self, data):
        lesson_ids = []
        for d in data:
            if d.get('lesson_id'):
                lesson_ids.append(d.get('lesson_id'))
        lessons = CourseLesson.objects.filter(id__in=lesson_ids).select_related('course').select_related('course__course_edition').only(
            'id', 'lesson_no', 'course__course_level', 'course__course_name', 'course__course_edition__edition_name'
        ).all()
        lesson_dict = {}
        for lesson in lessons:
            lesson_dict[lesson.id] = {
                'course_name': lesson.course.course_name,
                'course_level': lesson.course.course_level,
                'course_edition_name':  lesson.course.course_edition.edition_name,
                'lesson_no': lesson.lesson_no
            }
        for d in data:
            if d.get('lesson_id'):
                d['course_info'] = lesson_dict.get(d.get('lesson_id'))
            else:
                d['course_info'] = None
        return data

    def add_account_balance(self, data):
        parent_user_ids = []
        for d in data:
            parent_user_id = d.get('parent_user_id')
            if parent_user_id and parent_user_id not in parent_user_ids:
                parent_user_ids.append(parent_user_id)
        account_balances = AccountBalance.objects.filter(parent_user_id__in=parent_user_ids,
                                                         state=AccountBalance.NOT_DELETE).values(
            'parent_user_id', 'account_class').annotate(balance_sum=Sum('balance')).values('parent_user_id', 'account_class', 'balance_sum')
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
            parent_user_id = d.get('parent_user_id')
            account_balance_info = account_balance_dict.get(parent_user_id, {})
            d['balance'] = account_balance_info.get('normal_balance', 0)
            d['smallclass_count'] = account_balance_info.get('sg_balance', 0)
        return data

    def add_virtual_class_sum(self, data):
        student_user_ids = []
        for d in data:
            student_user_id = d.get('id')
            if student_user_id and student_user_id not in student_user_ids:
                student_user_ids.append(student_user_id)
        virtualclass_members = ScheduleVirtualclassMember.objects.filter(student_user_id__in=student_user_ids, virtual_class__status=VirtualclassInfo.FINISH_NOMAL).values('student_user_id').annotate(virtual_class_sum=Count('id')).values('student_user_id', 'virtual_class_sum')
        virtual_class_sum_dict = {}
        for virtualclass_member in virtualclass_members:
            student_user_id = virtualclass_member.get('student_user_id')
            virtual_class_sum = virtualclass_member.get('virtual_class_sum')
            virtual_class_sum_dict[student_user_id] = virtual_class_sum
        for d in data:
            student_user_id = d.get('id')
            virtual_class_sum = virtual_class_sum_dict.get(student_user_id, 0)
            d['virtual_class_sum'] = virtual_class_sum
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_account_balance(serializer.data)
            data = self.add_course_info(data)
            if 'warn' in self.request.path:
                for d in data:
                    d['balance'] = d['balance'] + d['smallclass_count']
            else:
                data = self.add_virtual_class_sum(data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def details(self, request, pk):
        student = UserStudentInfo.objects.select_related('parent_user').get(id=pk)
        studentserializer = StudentInfoSerializer(student)
        return Response(studentserializer.data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def edit_student(self, request, pk):
        real_name = request.data.get('real_name')
        birthday = request.data.get('birthday')
        student = UserStudentInfo.objects.filter(id=pk).first()
        if not student:
            return JsonResponse(code=1, msg='not found', status=status.HTTP_200_OK)
        if real_name:
            student.real_name = real_name
        if birthday:
            student.birthday = birthday
        student.save()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def course_info(self, request, pk):
        student = UserStudentInfo.objects.get(id=pk)
        now_time = utils.get_few_date_time()
        # 账户
        small_class_balance = AccountBalance.objects.filter(parent_user_id=student.parent_user_id, account_class=AccountBalance.PRIVATE_ACCOUNT).aggregate(balances=Sum('balance'))
        small_class_balance = small_class_balance['balances']
        if not student.lesson:
            return JsonResponse(code=1, msg='未定级', status=status.HTTP_200_OK)
        course_name = student.course.course_name
        course_level = student.course.course_level
        lesson_no = student.lesson_no
        course_edition_id = student.course_edition.id

        # 水平测试
        test_result = CourseAssessmentResult.objects.filter(student_user_id=pk).order_by('create_time').first()
        test_result_dict = {}
        if test_result:
            test_result_dict.update(
                id=test_result.id,
                course_name=test_result.course.course_name,
                course_edition_name=test_result.course.course_edition.edition_name,
                test_level=test_result.test_level
            )

        # 家长问卷
        parent_result = {}
        parent_question_result = CourseQuestionnaireResult.objects.filter(student_user_id=pk).order_by('create_time').first()
        if parent_question_result:
            course_edition = CourseEdition.objects.get(id=parent_question_result.edition)
            parent_result.update(
                course_edition_name=course_edition.edition_name,
                level=parent_question_result.level
            )
        balance = AccountBalance.objects.filter(parent_user_id=student.parent_user_id, account_class=AccountBalance.NORMAL_ACCOUNT).aggregate(balances=Sum('balance'))
        course_info = dict(
            course_name=course_name,
            course_level=course_level,
            lesson_no=lesson_no,
            course_edition_id=course_edition_id,
            balance=balance['balances'],
            smallclass_balance=small_class_balance,
            assessment_result=test_result_dict,
            parent_result=parent_result,
            allow_smallclass=student.allow_smallclass,
            only_smallclass=student.only_smallclass
        )
        return JsonResponse(code=0, msg='success', data=course_info, status=status.HTTP_200_OK)

    # 分配课程顾问
    @action(methods=['post'], detail=False)
    def distribut_adviser(self, request):

        student_id = request.data.get('student_id')
        course_adviser_id = request.data.get('course_adviser_id')
        try:
            student = UserStudentInfo.objects.get(id=student_id)
        except ObjectDoesNotExist as e:
            return JsonResponse(code=1, msg='未查询到该学生', status=status.HTTP_200_OK)
        course_adviser = UserInfo.objects.filter(id=course_adviser_id, role__id=RoleInfo.ADVISER_USER_ID).first()
        if not course_adviser:
            return JsonResponse(code=1, msg='未查询到该课程顾问', status=status.HTTP_200_OK)

        parent_user = student.parent_user
        if parent_user.adviser_user_id:
            return JsonResponse(code=1, msg='已经分配课程顾问', status=status.HTTP_200_OK)
        parent_user.adviser_user_id = course_adviser_id
        parent_user.adviser_user_name = course_adviser.realname
        parent_user.adviser_user_phone = course_adviser.phone
        parent_user.save()
        try:
            user = request.session.get('user')
            logger.debug('distribut adviser, user_id: {}, student_id: {}, course_adviser_id: {}'.format(user.get('id'), student_id, course_adviser_id))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', data={'name': course_adviser.realname, 'id': course_adviser.id}, status=status.HTTP_200_OK)

    # 更改课程顾问
    @action(methods=['put'], detail=True)
    def change_adviser(self, request, pk):
        course_adviser_id = request.data.get('course_adviser_id')
        course_adviser = UserInfo.objects.filter(id=course_adviser_id, role__id=RoleInfo.ADVISER_USER_ID).first()
        if not course_adviser:
            return JsonResponse(code=1, msg='未查询到该课程顾问', status=status.HTTP_200_OK)
        try:
            student = UserStudentInfo.objects.get(id=pk)
        except ObjectDoesNotExist as e:
            return JsonResponse(code=1, msg='未查询到该学生', status=status.HTTP_200_OK)

        parent_user = student.parent_user
        if not parent_user.adviser_user_id:
            return JsonResponse(code=1, msg='未分配课程顾问', status=status.HTTP_200_OK)
        parent_user.adviser_user_id = course_adviser_id
        parent_user.adviser_user_name = course_adviser.realname
        parent_user.adviser_user_phone = course_adviser.phone
        parent_user.save()
        try:
            user = request.session.get('user')
            logger.debug('change adviser, user_id: {}, student_id: {}, course_adviser_id: {}'.format(user.get('id'), pk, course_adviser_id))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', data={'name': course_adviser.realname, 'id': course_adviser.id}, status=status.HTTP_200_OK)

    # 批量添加课程顾问
    @action(methods=['post'], detail=False)
    def add_advisers(self, request):
        course_adviser_id = request.data.get('course_adviser_id')
        student_ids = request.data.get('student_ids')
        course_adviser = UserInfo.objects.filter(id=course_adviser_id, role__id=RoleInfo.ADVISER_USER_ID).first()
        if not course_adviser:
            return JsonResponse(code=1, msg='未查询到该课程顾问', status=status.HTTP_200_OK)

        for student_id in student_ids:
            try:
                student = UserStudentInfo.objects.get(id=student_id)
            except ObjectDoesNotExist as e:
                return JsonResponse(code=1, msg='未查询到学生'+ str(student_id), status=status.HTTP_200_OK)

            parent_user = student.parent_user
            # if parent_user.adviser_user_id:
            #     continue
            parent_user.adviser_user_id = course_adviser.id
            parent_user.adviser_user_name = course_adviser.realname
            parent_user.adviser_user_phone = course_adviser.phone
            parent_user.save()
            # student_parent_user = student.student_parent_user
            # if student_parent_user:
            #     student_parent_user.adviser_user_id = course_adviser_id
            #     student_parent_user.save()
        try:
            user = request.session.get('user')
            logger.debug(
                'add adviser, user_id: {}, student_ids: {}, course_adviser_id: {}'.format(user.get('id'), ','.join([str(student_id) for student_id in student_ids]), course_adviser_id))
        except Exception as e:
            pass
        return JsonResponse(code=0, msg='success', data={'name': course_adviser.realname, 'id': course_adviser.id}, status=status.HTTP_200_OK)

    # 重置密码
    @action(methods=['put'], detail=True)
    def resetpasswd(self, request, pk):

        student = UserStudentInfo.objects.get(id=pk)

        parent_user_id = student.parent_user_id

        set_password_url = 'http://' + settings.JAVA_DOMAIN + settings.UPDATE_USER_PASSWORD.format(user_id=parent_user_id, role=UserParentInfo.PARENT)

        params = {
            'newPassword': 'lingoace123',
            'oldPassword': 'lingoace123'
        }

        headers = {
            'Content-Type': 'application/json'
        }
        logger.debug('resetpasswd url: {}'.format(set_password_url))
        result = requests.put(set_password_url, data=json.dumps(params), headers=headers)
        result = result.json()
        logger.debug('resetpasswd result: {}'.format(result))
        if result.get('code', 0) != 200:
            return JsonResponse(code=1, msg='修改失败', status=status.HTTP_200_OK)
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 设置学生是否开启小班课
    @action(methods=['put'], detail=True)
    def set_allow_smallclass(self, request, pk):

        allow_smallclass = request.data.get('allow_smallclass')

        student = UserStudentInfo.objects.get(id=pk)

        student.allow_smallclass = allow_smallclass
        student.save()

        try:
            user = request.session.get('user')
            logger.debug('set allow smallclass user_id: {}, student_id: {}, allow_smallclass: {}'.format(user.get('id'), pk, allow_smallclass))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 设置学生是否上固定小班课
    @action(methods=['put'], detail=True)
    def set_only_smallclass(self, request, pk):

        only_smallclass = request.data.get('only_smallclass')

        student = UserStudentInfo.objects.get(id=pk)

        student.only_smallclass = only_smallclass
        student.save()

        try:
            user = request.session.get('user')
            logger.debug('set only smallclass user_id: {}, student_id: {}, only_smallclass: {}'.format(user.get('id'), pk, only_smallclass))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 设置学生等级
    @action(methods=['put'], detail=True)
    def set_student_lesson(self, request, pk):

        course_edition_id = request.data.get('course_edition_id')
        course_level = request.data.get('course_level')
        lesson_no = request.data.get('lesson_no')

        course_info = CourseInfo.objects.filter(course_edition_id=course_edition_id, course_level=course_level).first()

        if not course_info:
            return JsonResponse(code=1, msg='未找到匹配的课程信息', status=status.HTTP_200_OK)

        course_lesson = CourseLesson.objects.filter(course=course_info, lesson_no=lesson_no, status=CourseLesson.ACTIVE).first()

        if not course_lesson:
            return JsonResponse(code=1, msg='没有该节课', status=status.HTTP_200_OK)

        set_student_url = 'http://' + settings.JAVA_DOMAIN + settings.UPDATE_STUDENT_LESSON.format(student_user_id=pk, new_edition_id=course_edition_id, new_level=course_level, new_lesson_no=lesson_no)

        result = requests.put(set_student_url)

        result = result.json()

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='修改失败', status=status.HTTP_200_OK)

        try:
            user = request.session.get('user')
            logger.debug('set student lesson user_id: {}, student_id: {}, url: {}'.format(user.get('id'), pk, set_student_url))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 添加推荐人
    @action(methods=['put'], detail=True)
    def add_reference(self, request, pk):

        return JsonResponse(code=1, msg='该功能暂时不可用', status=status.HTTP_200_OK)

        username = request.data.get('username')

        student = UserStudentInfo.objects.get(id=pk)

        parent = student.parent_user

        if parent.referrer_user_id:
            return JsonResponse(code=1, msg='该用户已有推荐人', status=status.HTTP_200_OK)

        reference_parent = UserParentInfo.objects.filter(Q(username=username)|Q(email=username)|Q(phone=username)).first()

        if parent.id == reference_parent.id:
            return JsonResponse(code=1, msg='不能设自己为推荐人', status=status.HTTP_200_OK)

        if reference_parent.referrer_user_id == parent.id:
            return JsonResponse(code=1, msg='不能互设推荐人', status=status.HTTP_200_OK)

        if not reference_parent:
            return JsonResponse(code=1, msg='未查到该推荐人', status=status.HTTP_200_OK)

        recharge_order = RechargeOrder.objects.filter(parent_user=reference_parent, status=RechargeOrder.PAID).first()

        if not recharge_order:
            return JsonResponse(code=1, msg='推荐人未充值，设置不成功', status=status.HTTP_200_OK)

        parent.referrer_user_id = reference_parent.id
        parent.referrer_user_name = reference_parent.real_name
        parent.referrer_user_identify = reference_parent.__str__()
        parent.save()

        balance_change = BalanceChange.objects.filter(parent_user_id=parent.id, reason=BalanceChange.REFERRAL_INCENTIVE).first()

        if balance_change:
            return JsonResponse(code=1, msg='已存在推荐人奖励', status=status.HTTP_200_OK)

        recharge_order = RechargeOrder.objects.filter(parent_user=parent, status=RechargeOrder.PAID).order_by('-create_time').first()

        if not recharge_order:
            return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

        reference_recharge_amount = RechargeOrder.objects.filter(parent_user=parent, status=RechargeOrder.PAID).aggregate(nums=Sum('recharge_amount'))

        # 推荐人规则修改
        now_time = timezone.now()
        recharge_amount = reference_recharge_amount.get('nums', 0)
        incentive_rule_formula = CommonRuleFormula.objects.filter(min_amount__lte=recharge_amount,
                                         max_amount__gt=recharge_amount,
                                         rule__valid_start__lte=now_time,
                                         rule__valid_end__gt=now_time,
                                         rule__rule_type=CommonBussinessRule.REFERRAL_INCENTIVE).first()

        if incentive_rule_formula:
            reference_incentive_balance_change = BalanceChange()
            reference_incentive_balance_change.role = BalanceChange.PARENT
            reference_incentive_balance_change.user_id = parent.id
            reference_incentive_balance_change.parent_user_id = parent.id
            reference_incentive_balance_change.amount = incentive_rule_formula.amount
            reference_incentive_balance_change.reason = BalanceChange.REFERRAL_INCENTIVE
            reference_incentive_balance_change.adviser_user_id = parent.adviser_user_id
            reference_incentive_balance_change.xg_user_id = parent.xg_user_id
            reference_incentive_balance_change.reference = recharge_order.order_no
            reference_incentive_balance_change.save()

        rule_formula = CommonRuleFormula.objects.filter(min_amount__lte=recharge_amount,
                                                        max_amount__gt=recharge_amount,
                                                        rule__valid_start__lte=now_time,
                                                        rule__valid_end__gt=now_time,
                                                        rule__rule_type=CommonBussinessRule.REFERRAL_BONUS).first()
        if rule_formula:
            reference_balance_change = BalanceChange()
            reference_balance_change.role = BalanceChange.PARENT
            reference_balance_change.user_id = parent.id
            reference_balance_change.parent_user_id = reference_parent.id
            reference_balance_change.amount = rule_formula.amount
            reference_balance_change.reason = BalanceChange.REFERRAL
            reference_balance_change.adviser_user_id = reference_parent.adviser_user_id
            reference_balance_change.xg_user_id = reference_parent.xg_user_id
            reference_balance_change.reference = recharge_order.order_no
            reference_balance_change.save()
        try:
            user = request.session.get('user')
            logger.debug('add reference  user_id: {}, student_id: {}, reference_parent_id: {}'.format(user.get('id'), pk, reference_parent.id))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    # 下载
    @action(methods=['get'], detail=False)
    def downloads(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return JsonResponse(code=0, msg='success', data=serializer.data, status=status.HTTP_200_OK)

    # 常用老师接口
    @action(methods=['get'], detail=True)
    def often_tutor(self, request, pk):

        page = request.query_params.get('page')
        page_size = request.query_params.get('page_size')
        class_type_id = request.query_params.get('class_type_id')

        often_tutor_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_OFTEN_TUTOR.format(student_user_id=pk, class_type_id=class_type_id, page=page, page_size=page_size)

        result = utils.fetch_get_api(often_tutor_url)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='获取常用老师失败,{}'.format(result.get('message', '')), data=result.get('data', []), status=status.HTTP_200_OK)

        tutor_list = result.get('data', {}).get('list', [])

        tutor_ids = [tutor.get('userId') for tutor in tutor_list]

        month_ago = timezone.now() - timedelta(days=30)  # 30天之内的学生

        tutors = TutorInfo.objects.filter(id__in=tutor_ids).all().extra(
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
        )

        tutors = tutors.prefetch_related('tutor_course').prefetch_related('tutor_course__course').prefetch_related('tutor_course__course__course_edition')

        serailizers = StudentAbleTutorSerializer(tutors, many=True)

        result['data']['list'] = serailizers.data

        return JsonResponse(code=0, msg='success', data=result.get('data', {}), status=status.HTTP_200_OK)

    # 可教老师接口
    @action(methods=['get'], detail=True)
    def able_tutor(self, request, pk):

        page = request.query_params.get('page')
        page_size = request.query_params.get('page_size')
        class_type_id = request.query_params.get('class_type_id')
        prefer_time = request.query_params.get('prefer_time')

        able_tutor_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_ABLE_TUTOR.format(student_user_id=pk, class_type_id=class_type_id, page=page, page_size=page_size)

        data = {
            'preferTime': prefer_time
        }

        result = utils.fetch_get_api(able_tutor_url, data=data)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='{}'.format(result.get('message', '')),
                                data=result.get('data', []), status=status.HTTP_200_OK)

        tutor_list = result.get('data', {}).get('list', [])

        tutor_ids = [tutor.get('userId') for tutor in tutor_list]

        month_ago = timezone.now() - timedelta(days=30)  # 30天之内的学生

        tutors = TutorInfo.objects.filter(id__in=tutor_ids).all().extra(
            select={
                'student_sum': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                        left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                        where cvi.tutor_user_id=user_tutor_info.id and cvi.status in ({}, {}, {})'''.format(
                    VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED, VirtualclassInfo.FINISH_NOMAL)
            }
        ).extra(
            select={
                'student_num': '''select count(distinct svm.student_user_id) from schedule_virtualclass_member svm 
                        left join classroom_virtualclass_info cvi on  svm.virtual_class_id=cvi.id 
                        where cvi.tutor_user_id=user_tutor_info.id and cvi.start_time>='{}' and cvi.status in ({}, {}, {})'''.format(
                    utils.datetime_str(month_ago), VirtualclassInfo.NOT_START, VirtualclassInfo.STARTED,
                    VirtualclassInfo.FINISH_NOMAL)
            }
        )
        tutors = tutors.prefetch_related('tutor_course').prefetch_related('tutor_course__course').prefetch_related('tutor_course__course__course_edition')

        serailizers = StudentAbleTutorSerializer(tutors, many=True)

        result['data']['list'] = serailizers.data

        return JsonResponse(code=0, msg='success', data=result.get('data', {}), status=status.HTTP_200_OK)

    # 学生课表
    @action(methods=['get'], detail=True)
    def timetable(self, request, pk):

        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        student_timetable_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_TIMETABLE.format(student_user_id=pk, start_time=start_time, end_time=end_time)

        result = utils.fetch_get_api(student_timetable_url)

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='{}'.format(result.get('message', '')),
                                data=result.get('data', []), status=status.HTTP_200_OK)

        return JsonResponse(code=0, msg='success', data=result.get('data', []), status=status.HTTP_200_OK)

    # 约课 取消课
    @action(methods=['post'], detail=False)
    def subscribe(self, request):

        class_type_id = request.data.get('class_type_id')
        end_recurring_time = request.data.get('end_recurring_time')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        student_user_id =request.data.get('student_user_id')
        tutor_user_id =request.data.get('tutor_user_id')
        op_type = request.data.get('op_type')

        student_subscribe_url = 'http://' + settings.JAVA_DOMAIN + settings.STUDENT_APPOINTMENT

        user = request.session.get('user')

        data = {
            "classId": 0,
            "classTypeId": class_type_id,
            "endRecurringTime": end_recurring_time,
            "endTime": end_time,
            "opType": op_type,  # 1：预约时间；2：取消预约
            "startTime": start_time,
            "studentUserId": student_user_id,
            "tutorUserId": tutor_user_id,
            "opUserId": user.get('id')
        }

        result = utils.fetch_post_api(student_subscribe_url, data, user.get('id'))

        if result.get('code') != 200:
            return JsonResponse(code=1, msg='{}'.format(result.get('message', '')),
                                data=result.get('data', []), status=status.HTTP_200_OK)
        try:
            logger.debug('student timetable edit, operate user: {}, operate_type: {}, student_user_id: {}, start_time: {}, end_time: {}'.format(user.get('id'), op_type, student_user_id, start_time, end_time))
        except Exception as e:
            logger.debug('record log fail, error={}'.format(e))
        return JsonResponse(code=0, msg='success', data=result.get('data', []), status=status.HTTP_200_OK)


class OldStudentManagerViewSet(viewsets.ModelViewSet):

    serializer_class = OldStudentSerializer
    pagination_class = LargeResultsSetPagination
    filter_class = OldStudentManagerFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, StudentFilterBackend)

    ordering_fields = ('create_time', 'parent_user__balance', 'virtual_class_sum', 'smallclass_count')

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

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action == 'list':
            permissions.append(OldStudentListPermission())
        return permissions

    def get_serializer_context(self):

        if self.action == 'list':
            users = UserInfo.objects.all().only('id', 'username', 'realname')
            result = {}
            for user in users:
                result[user.id] = user
            return {
                'request': self.request,
                'format': self.format_kwarg,
                'user_infos': result
            }

    def get_queryset(self):
        start, end = utils.getNowMonth()

        queryset = UserStudentInfo.objects.all()
        queryset = queryset.select_related('parent_user').only('id',
                                                               'parent_user_id',
                                                               'real_name',
                                                               'create_time',
                                                               'first_course',
                                                               'lesson_id',
                                                               'parent_user__adviser_user_id',
                                                               'parent_user__xg_user_id',
                                                               'parent_user__username',
                                                               'parent_user__email',
                                                               'parent_user__phone',
                                                               'parent_user__code',
                                                               'parent_user__referrer_user_id',
                                                               'parent_user__nationality',
                                                               'parent_user__currency',
                                                               'parent_user__login_tz',
                                                               'parent_user__referrer_user_name',
                                                               'parent_user__referrer_user_identify',
                                                               'parent_user__login_time',
                                                               'parent_user__wechat',
                                                               'parent_user__whatsapp',
                                                               'parent_user__country_of_residence'
                                                               )
        return queryset

    def add_virtual_class_sum(self, data):
        student_user_ids = []
        for d in data:
            student_user_id = d.get('id')
            if student_user_id and student_user_id not in student_user_ids:
                student_user_ids.append(student_user_id)
        balance_changes = BalanceChange.objects.filter(user_id__in=student_user_ids, reason=BalanceChange.AD_HOC).values('user_id').annotate(virtual_class_sum=Count('id')).values('user_id', 'virtual_class_sum')
        virtual_class_sum_dict = {}
        for balance_change in balance_changes:
            user_id = balance_change.get('user_id')
            virtual_class_sum = balance_change.get('virtual_class_sum')
            virtual_class_sum_dict[user_id] = virtual_class_sum
        for d in data:
            student_user_id = d.get('id')
            virtual_class_sum = virtual_class_sum_dict.get(student_user_id, 0)
            d['virtual_class_sum'] = virtual_class_sum
        return data

    def add_lesson_sum(self, data):
        start, end = utils.getNowMonth()
        student_user_ids = []
        for d in data:
            student_user_id = d.get('id')
            if student_user_id and student_user_id not in student_user_ids:
                student_user_ids.append(student_user_id)
        #         'lesson_sum': """select count(*) from classroom_virtualclass_info cvi right join schedule_virtualclass_member svm on svm.virtual_class_id=cvi.id where cvi.start_time>='{}' and cvi.start_time<='{}' and cvi.status={} and svm.student_user_id=user_student_info.id""".format(start_time_str, end_time_str, VirtualclassInfo.FINISH_NOMAL)
        the_month_virtual_sums = ScheduleVirtualclassMember.objects.filter(student_user_id__in=student_user_ids, virtual_class__start_time__gte=start, virtual_class__start_time__lte=end, virtual_class__status=VirtualclassInfo.FINISH_NOMAL).values('student_user_id').annotate(lesson_sum=Count('virtual_class_id')).values('student_user_id', 'lesson_sum')
        the_month_virtual_sum_dict = {}
        for the_month_virtual_sum in the_month_virtual_sums:
            student_user_id = the_month_virtual_sum.get('student_user_id')
            lesson_sum = the_month_virtual_sum.get('lesson_sum')
            the_month_virtual_sum_dict[student_user_id] = lesson_sum
        for d in data:
            student_user_id = d.get('id')
            lesson_sum = the_month_virtual_sum_dict.get(student_user_id, 0)
            d['lesson_sum'] = lesson_sum
        return data

    def add_account_balance(self, data):
        parent_user_ids = []
        for d in data:
            parent_user_id = d.get('parent_user').get('id')
            if parent_user_id and parent_user_id not in parent_user_ids:
                parent_user_ids.append(parent_user_id)
        account_balances = AccountBalance.objects.filter(parent_user_id__in=parent_user_ids,
                                                         state=AccountBalance.NOT_DELETE).values(
            'parent_user_id', 'account_class').annotate(balance_sum=Sum('balance')).values('parent_user_id', 'account_class', 'balance_sum')
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
            parent_user_id = d.get('parent_user').get('id')
            account_balance_info = account_balance_dict.get(parent_user_id, {})
            d.get('parent_user')['balance'] = account_balance_info.get('normal_balance', 0)
            d.get('parent_user')['small_class_balance'] = account_balance_info.get('sg_balance', 0)
        return data

    def add_course_info(self, data):
        lesson_ids = []
        for d in data:
            if d.get('lesson_id'):
                lesson_ids.append(d.get('lesson_id'))
        lessons = CourseLesson.objects.filter(id__in=lesson_ids).select_related('course').select_related('course__course_edition').only(
            'id', 'lesson_no', 'course__course_level', 'course__course_name', 'course__course_edition__edition_name'
        ).all()
        lesson_dict = {}
        for lesson in lessons:
            lesson_dict[lesson.id] = {
                'course_name': lesson.course.course_name,
                'course_level': lesson.course.course_level,
                'course_edition_name':  lesson.course.course_edition.edition_name,
                'lesson_no': lesson.lesson_no
            }
        for d in data:
            if d.get('lesson_id'):
                d['course_info'] = lesson_dict.get(d.get('lesson_id'))
            else:
                d['course_info'] = None
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_account_balance(serializer.data)
            # data = self.add_virtual_class_sum(data)
            data = self.add_lesson_sum(data)
            data = self.add_course_info(data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 分配学管老师
    @action(methods=['post'], detail=False)
    def distribut_learnmanager(self, request):

        student_id = request.data.get('student_id')
        learn_manager_id = request.data.get('learn_manager_id')
        try:
            student = UserStudentInfo.objects.get(id=student_id)
        except ObjectDoesNotExist as e:
            return JsonResponse(code=1, msg='未查询到该学生', status=status.HTTP_200_OK)
        learn_manager = UserInfo.objects.filter(id=learn_manager_id, role__id=RoleInfo.XG_USER_ID).first()
        if not learn_manager:
            return JsonResponse(code=1, msg='未查询到该学管老师', status=status.HTTP_200_OK)
        parent_user = student.parent_user
        if parent_user.xg_user_id:
            return JsonResponse(code=1, msg='已经分配学管老师', status=status.HTTP_200_OK)
        parent_user.xg_user_id = learn_manager.id
        parent_user.xg_user_name = learn_manager.realname
        parent_user.xg_user_phone = learn_manager.phone
        parent_user.save()

        try:
            user = request.session.get('user')
            logger.debug('distribut learnmanager  user_id: {}, student_id: {}, learn_manager_id: {}'.format(user.get('id'), student_id, learn_manager_id))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', data={'name': learn_manager.realname, 'id': learn_manager.id}, status=status.HTTP_200_OK)

    # 更改学管老师
    @action(methods=['put'], detail=True)
    def change_learnmanager(self, request, pk):
        learn_manager_id = request.data.get('learn_manager_id')
        learn_manager = UserInfo.objects.filter(id=learn_manager_id, role__id=RoleInfo.XG_USER_ID).first()
        if not learn_manager:
            return JsonResponse(code=1, msg='未查询到该学管老师', status=status.HTTP_200_OK)
        student = UserStudentInfo.objects.get(id=pk)
        parent_user = student.parent_user
        if not parent_user.xg_user_id:
            return JsonResponse(code=1, msg='未分配学管老师', status=status.HTTP_200_OK)
        parent_user.xg_user_id = learn_manager.id
        parent_user.xg_user_name = learn_manager.realname
        parent_user.xg_user_phone = learn_manager.phone
        parent_user.save()

        try:
            user = request.session.get('user')
            logger.debug('change learnmanager  user_id: {}, student_id: {}, learn_manager_id: {}'.format(user.get('id'), pk, learn_manager_id))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', data={'name': learn_manager.realname, 'id': learn_manager.id}, status=status.HTTP_200_OK)

    # 批量添加学管
    @action(methods=['post'], detail=False)
    def add_learnmanagers(self, request):
        learn_manager_id = request.data.get('learn_manager_id')
        student_ids = request.data.get('student_ids')
        learn_manager = UserInfo.objects.filter(id=learn_manager_id, role__id=RoleInfo.XG_USER_ID).first()
        if not learn_manager:
            return JsonResponse(code=1, msg='未查询到该学管', status=status.HTTP_200_OK)

        for student_id in student_ids:

            student = UserStudentInfo.objects.get(id=student_id)

            parent_user = student.parent_user

            parent_user.xg_user_id = learn_manager.id
            parent_user.xg_user_name = learn_manager.realname
            parent_user.xg_user_name = learn_manager.realname
            parent_user.xg_user_phone = learn_manager.phone
            parent_user.save()

        try:
            user = request.session.get('user')
            logger.debug('add learnmanagers  user_id: {}, student_ids: {}, learn_manager_id: {}'.format(user.get('id'), ','.join([str(student_id) for student_id in student_ids]), learn_manager_id))
        except Exception as e:
            pass

        return JsonResponse(code=0, msg='success', data={'name': learn_manager.realname, 'id': learn_manager.id}, status=status.HTTP_200_OK)


class ExtStudentViewSet(viewsets.ModelViewSet):

    permissions = [IsAuthenticated(), ]

    def get_object(self):
        ext_student_id = self.kwargs.get('pk')
        try:
            obj = ExtStudent.objects.get(student_id=ext_student_id)
        except ObjectDoesNotExist as e:
            obj = None
        return obj

    def get_queryset(self):
        return ExtStudent.objects.all()

    def get_serializer_class(self):
        #
        if self.action == 'update':
            return ExtStudentUpdateSerializer

        if self.action == 'create':
            return ExtStudentUpdateSerializer

        if self.action == 'add':
            return ExtStudentUpdateSerializer
        return ExtStudentSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        user = request.session.get('user')
        id = request.data.get('id')
        if user:
            request.data["edit_user_id"] = user.get('id')
        if id:
            ext_user = ExtStudent.objects.filter(id=id).update(**request.data)
        else:
            ext_user = ExtStudent.objects.create(**request.data)
        return Response(status=status.HTTP_200_OK)


class RemarkViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = StudentRemark.objects.all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset.order_by('-create_time')

    def get_serializer_class(self):

        if self.action == 'list':
            return RemarkListSerializer
        return RemarkSerializer

    def create(self, request, *args, **kwargs):
        user = request.session.get('user')
        request.data['user'] = user.get('id')
        return super().create(request, *args, **kwargs)


class SmallClassStudentViewSet(viewsets.ModelViewSet):

    serializer_class = SmallClassStudentSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = StudentManagerFilter

    def get_queryset(self):

        queryset = UserStudentInfo.objects.filter(status=UserStudentInfo.ACTIVE).all()

        queryset = queryset.select_related('parent_user')

        queryset = queryset.only('id', 'real_name', 'birthday', 'gender',
                                 'parent_user__id', 'parent_user__username', 'parent_user__phone', 'parent_user__email',
                                 'parent_user__adviser_user_id', 'parent_user__xg_user_id',
                                 'parent_user__country_of_residence')
        return queryset

    def add_adviser_user_name(self, data):
        adviser_user_ids = []
        for d in data:
            adviser_user_id = d.get('parent_user').get('adviser_user_id')
            if adviser_user_id and adviser_user_id not in adviser_user_ids:
                adviser_user_ids.append(adviser_user_id)
        user_infos = UserInfo.objects.filter(id__in=adviser_user_ids).all().only('id', 'realname')
        user_info_dict = {}
        for user_info in user_infos:
            user_info_dict[user_info.id] = user_info
        for s in data:
            user_info_instance = user_info_dict.get(s.get('parent_user').get('adviser_user_id'))
            if user_info_instance:
                s.get('parent_user')['adviser_user_name'] = user_info_instance.realname
            else:
                s.get('parent_user')['adviser_user_name'] = None
        return data

    def add_account_balance(self, data):
        parent_user_ids = []
        for d in data:
            parent_user_id = d.get('parent_user').get('id')
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
            parent_user_id = d.get('parent_user').get('id')
            account_balance_info = account_balance_dict.get(parent_user_id, {})
            d.get('parent_user')['normal_balance'] = account_balance_info.get('normal_balance', 0)
            d.get('parent_user')['sg_balance'] = account_balance_info.get('sg_balance', 0)
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_adviser_user_name(serializer.data)
            data = self.add_account_balance(data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
