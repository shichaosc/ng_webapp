from webapp.models import *
from django.core.management.base import BaseCommand
from course.models import CourseLesson, CourseHomework, \
    Courseware as NewCourseware, CourseAssessmentQuestion, CourseExtcourseTag, CourseExtcourse, \
    CourseExtcourseware, CourseExtcourseOptag, CourseEdition, CourseInfo, CourseQuestionnaire, \
    CourseTeacherGuidebook
from common.models import ExchangeRate as CommonExchangeRate, CommonCoupon, CommonBussinessRule, \
    CommonRuleFormula, CommonAmbassadorCode
from django.conf import settings
from finance.models import ClasstypePrice
from webapp.utils import print_insert_table_times
from tutor.models import UserLevel
import math
import multiprocessing
from django.db import connections
import os
from django.db.models import Max
from webapp.app_settings import CURRENCY_CHOICES
from django.db import connections
from student.models import UserParentInfo, UserStudentInfo
from finance.models import BalanceChangeNew
from classroom.models import VirtualclassInfo
from scheduler.models import ScheduleVirtualclassMember


class Command(BaseCommand):


    def handle(self, *args, **options):

        sql = '''select tmp.*, tmp.parent_balance-tmp.fbc_amount_sum as gaps from (
                    select 
                            distinct
                            upi.id,
                            upi.create_time,
                            upi.username,
                            upi.real_name,
                            (upi.balance + upi.bonus_balance + upi.sg_balance) as parent_balance,
                            (select sum(fbc.amount) from finance_balance_change fbc where fbc.parent_user_id=upi.id) as fbc_amount_sum
                    -- 		((select sum(fbc.amount) from finance_balance_change fbc where fbc.parent_user_id=upi.id) - (upi.balance + upi.bonus_balance + upi.sg_balance)) as gaps
                    from user_parent_info upi 
                    left join user_student_info usi on upi.id=usi.parent_user_id
                    where upi.is_staff<>1 and upi.status=1 and usi.id is not null) tmp
                    where (tmp.parent_balance-tmp.fbc_amount_sum)<>0  and tmp.create_time<'2020-01-15 00:00:00' order by tmp.create_time'''

        usernames = []
        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                usernames.append(row[2])
            cursor.close()

        for username in usernames:

            if username == 'huaqing':
                old_username = '熊偌彤'
            elif username == 'hanqing':
                old_username = '熊梓博'
            elif username == 'ivy1688':
                old_username = 'lvy'
            # elif username == 'xunmei02@gmail.com':
            #     old_username = ['雅雅', '璐璐']
            else:
                old_username = username
            auth_user = User.objects.filter(username=old_username).first()

            if not auth_user:
                print('not found user, username: {}, old_username: {}'.format(username, old_username))
                continue

            user_parent_info = UserParentInfo.objects.filter(username=username).first()

            abcs = AccountBalanceChange.objects.filter(user_id=auth_user.id).all()

            for abc in abcs:
                balance_change = BalanceChangeNew.objects.filter(parent_user_id=user_parent_info.id, amount=abc.amount, create_time=abc.created_on, reason=abc.reason).first()

                if balance_change:
                    continue
                # else:
                #     print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                #     continue

                if user_parent_info.create_time > abc.created_on:

                    print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                    continue

                if abc.reason == AccountBalanceChange.TRANSFER_OUT:  # 转出

                    abc_new = BalanceChangeNew()
                    abc_new.reason = BalanceChangeNew.TRANSFER_OUT
                    abc_new.parent_user_id = user_parent_info.id
                    abc_new.user_id = user_parent_info.id
                    abc_new.amount = abc.amount
                    abc_new.create_time = abc.created_on
                    abc_new.update_time = abc.updated_on
                    abc_new.role = BalanceChangeNew.PARENT
                    abc_new.reference = abc.reference
                    abc_new.normal_amount = 0

                    sql = '''insert into finance_balance_change(reason, parent_user_id, user_id, amount, role, reference, normal_amount, create_time, update_time)
                                                        values({}, {}, {}, {}, {}, {}, {}, '{}', '{}');'''.format(
                        abc.reason, abc_new.parent_user_id, abc_new.user_id, abc.amount, BalanceChangeNew.PARENT, abc.reference, 0,
                        abc.created_on.strftime('%Y-%m-%d %H:%M:%S'), abc.updated_on.strftime('%Y-%m-%d %H:%M:%S'))
                    print(sql)
                    continue


                if abc.reason == AccountBalanceChange.FREE_TRIAL:
                    '''reason 6缺失数据'''
                    student = UserStudentInfo.objects.filter(parent_user_id=user_parent_info.id,
                                                             student_parent_user_id=user_parent_info.id).first()
                    abc_new = BalanceChangeNew()
                    abc_new.reason = BalanceChangeNew.FREE_TRIAL
                    abc_new.parent_user_id = user_parent_info.id
                    abc_new.user_id = student.id
                    abc_new.amount = abc.amount
                    abc_new.create_time = abc.created_on
                    abc_new.update_time = abc.updated_on
                    abc_new.role = BalanceChangeNew.PARENT
                    abc_new.reference = abc.reference
                    abc_new.normal_amount = 0
                    # abc_new.save()

                    sql = '''insert into finance_balance_change(reason, parent_user_id, user_id, amount, role, reference, normal_amount, create_time, update_time)
                                                        values({}, {}, {}, {}, {}, {}, {}, '{}', '{}');'''.format(abc.reason, user_parent_info.id, student.id, abc.amount, BalanceChangeNew.PARENT, abc.reference, 0, abc.created_on.strftime('%Y-%m-%d %H:%M:%S'), abc.updated_on.strftime('%Y-%m-%d %H:%M:%S'))
                    print(sql)
                    continue

                if abc.reason in (AccountBalanceChange.ABSENCE_PENALTY, AccountBalanceChange.NO_SHOW_COMPENSATION, AccountBalanceChange.ABSENCE_COMPENSATION, AccountBalanceChange.NO_SHOW_PENALTY):

                    if abc.reference == 0:
                        print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                        continue

                    vc_info_id = self.get_virtualclass_info(abc.reference, user_parent_info.id)

                    if not vc_info_id:
                        print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                        continue

                    virtualclass_member = ScheduleVirtualclassMember.objects.filter(virtual_class_id=vc_info_id, student_user__parent_user_id=user_parent_info.id).first()

                    abc_new = BalanceChangeNew()

                    if abc.amount > 0:
                        abc_new.reason = BalanceChangeNew.NO_SHOW_COMPENSATION
                    elif abc.amount < 0:
                        abc_new.reason = BalanceChangeNew.ABSENCE_PENALTY

                    abc_new.parent_user_id = user_parent_info.id
                    abc_new.user_id = virtualclass_member.student_user.id
                    abc_new.amount = abc.amount
                    abc_new.create_time = abc.created_on
                    abc_new.update_time = abc.updated_on
                    abc_new.role = BalanceChangeNew.PARENT
                    abc_new.reference = vc_info_id
                    abc_new.normal_amount = 0

                    sql = '''insert into finance_balance_change(reason, parent_user_id, user_id, amount, role, reference, normal_amount, create_time, update_time)
                                                        values({}, {}, {}, {}, {}, {}, {}, '{}', '{}');'''.format(
                        abc_new.reason, user_parent_info.id, abc_new.user_id, abc.amount, BalanceChangeNew.CHILDREN,
                        abc_new.reference, 0, abc.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                        abc.updated_on.strftime('%Y-%m-%d %H:%M:%S'))
                    print(sql)
                    continue

                if abc.reason == AccountBalanceChange.AD_HOC:

                    if abc.reference == 0:
                        print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                        continue

                    vc_info_id = self.get_virtualclass_info(abc.reference, user_parent_info.id)

                    if not vc_info_id:
                        print("user_id: {}, parent_user_id: {}, username: {}, abc_id: {}, amount: {}, reason: {}, reference: {}, create_time: {}, update_time: {}".format(auth_user.id, user_parent_info.id, username, abc.id, abc.amount, abc.reason, abc.reference, abc.created_on, abc.updated_on))
                        continue
                    virtualclass_member = ScheduleVirtualclassMember.objects.filter(virtual_class_id=vc_info_id, student_user__parent_user_id=user_parent_info.id).first()
                    abc_new = BalanceChangeNew()

                    abc_new.parent_user_id = user_parent_info.id
                    abc_new.user_id = virtualclass_member.student_user.id
                    abc_new.reason = abc.reason
                    abc_new.amount = abc.amount
                    abc_new.create_time = abc.created_on
                    abc_new.update_time = abc.updated_on
                    abc_new.role = BalanceChangeNew.PARENT
                    abc_new.reference = vc_info_id
                    abc_new.normal_amount = 0

                    sql = '''insert into finance_balance_change(reason, parent_user_id, user_id, amount, role, reference, normal_amount, create_time, update_time)
                                                        values({}, {}, {}, {}, {}, {}, {}, '{}', '{}');'''.format(
                        abc_new.reason, user_parent_info.id, abc_new.user_id, abc.amount, BalanceChangeNew.CHILDREN,
                        abc_new.reference, 0, abc.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                        abc.updated_on.strftime('%Y-%m-%d %H:%M:%S'))
                    print(sql)
                    continue

                if abc.reason == AccountBalanceChange.NO_REASON:
                    sql = '''insert into finance_balance_change(reason, parent_user_id, user_id, amount, role, reference, normal_amount, create_time, update_time)
                                                        values({}, {}, {}, {}, {}, {}, {}, '{}', '{}');'''.format(BalanceChangeNew.COMPENSATION, user_parent_info.id, user_parent_info.id, abc.amount, BalanceChangeNew.PARENT, abc.reference, 0, abc.created_on.strftime('%Y-%m-%d %H:%M:%S'), abc.updated_on.strftime('%Y-%m-%d %H:%M:%S'))
                    print(sql)
                    continue


    def get_virtualclass_info(self, vc_id, parent_user_id):

        vc = VirtualClass.objects.filter(id=vc_id).first()

        if not vc:
            return None

        schedule_time = vc.appointment.scheduled_time

        vc_info =VirtualclassInfo.objects.filter(start_time=schedule_time, virtual_class_member__student_user__parent_user_id=parent_user_id).first()

        if vc_info:
            return vc_info.id
        return None
