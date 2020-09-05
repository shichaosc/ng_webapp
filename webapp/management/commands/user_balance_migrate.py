from django.core.management.base import BaseCommand
from student.models import UserParentInfo
from finance.models import AccountBalance, RechargeOrder, BalanceChangeNew
from django.db.models import Q, Sum, F
from classroom.models import VirtualclassInfo, ClassType
from course.models import CourseEdition
from django.db import models
from django.db import connections
import time
import functools


def print_insert_table_times(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(func.__name__, '运行时间={}'.format(end_time-start_time))
        return result
    return wrapper


'''
迁移用户账户
1. 迁移accounts_balance,  rate计算方式：
    (1): 普通balance: finance_recharge_order表sg_class是空的数据，支付成功-退款，sum(total_price)/sum(total_amount)
    (2): sg balance: finance_recharge_order表sg_class有数据，支付成功-退款，sum(total_price)/sum(total_amount)
    (3): 推荐人balance    
'''


class Command(BaseCommand):

    def calculate_rate(self):

        normal_price = 0
        normal_amount = 0

        normal_amount_sql = '''select sum(amount) from finance_balance_change fbc 
                                left join user_parent_info upi on fbc.parent_user_id=upi.id 
                                where upi.is_staff<>1 and fbc.reason in(3,4,18,5,10,11,6,12,19,16,15)'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(normal_amount_sql)
            rows = cursor.fetchall()
            for row in rows:
                normal_amount = row[0]
            cursor.close()

        noral_price_sql = '''select sum(fro.total_price/cer.rate*210) from finance_recharge_order fro 
                                left join user_parent_info upi on fro.parent_user_id=upi.id
                                left join common_exchange_rate cer on cer.id=fro.currency_id
                                where upi.is_staff<>1 and fro.status in (1, 3)'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(noral_price_sql)
            rows = cursor.fetchall()
            for row in rows:
                normal_price = row[0]
            cursor.close()

        sg_info_sql = '''select sum(fro.total_price/cer.rate*210), sum(fro.total_amount),fro.status from finance_recharge_order fro 
                            left join user_parent_info upi on fro.parent_user_id=upi.id
                            left join common_exchange_rate cer on cer.id=fro.currency_id
                            where upi.is_staff<>1 and fro.status in (1, 3) and fro.currency='SGD' and fro.rate=30
                            group by fro.status'''

        sg_price = 0
        sg_amount = 0

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sg_info_sql)
            rows = cursor.fetchall()
            print(rows)
            for row in rows:
                sg_price = sg_price + row[0]
                if row[2] == 1:  #  支付成功
                    sg_amount = sg_amount + row[1]
                else:
                    sg_amount = sg_amount - row[1]
            cursor.close()

        normal_amount = normal_amount - sg_amount
        normal_price = normal_price - sg_price
        normal_rate = 0
        sg_rate = 0

        if normal_amount:
            normal_rate = normal_price/(normal_amount*210)

        if sg_amount:
            sg_rate = sg_price / (sg_amount * 210)

        return normal_rate, sg_rate

    @print_insert_table_times
    def handle(self, *args, **options):

        parents = UserParentInfo.objects.filter().all()

        normal_rate, sg_rate = self.calculate_rate()
        print(normal_rate, sg_rate, '\n')

        AccountBalance.objects.all().delete()

        for parent in parents:
            print(parent.id, '\n')

            charge_balance_change = BalanceChangeNew.objects.filter(parent_user_id=parent.id, reason__in=(BalanceChangeNew.TOP_UP, BalanceChangeNew.BONUS, BalanceChangeNew.TRANSFER_IN, BalanceChangeNew.TRANSFER_OUT)).first()

            if charge_balance_change:
                type = AccountBalance.TOPUP_AMOUNT
                balance_rate = normal_rate
            else:
                type = AccountBalance.BONUS_AMOUNT
                balance_rate = 0
            normal_balance = AccountBalance()
            normal_balance.parent_user_id = parent.id
            normal_balance.type = type
            normal_balance.account_class = AccountBalance.NORMAL_ACCOUNT
            normal_balance.balance = parent.balance + parent.bonus_balance
            normal_balance.rate = balance_rate
            normal_balance.save()

            sg_balance = AccountBalance()
            sg_balance.parent_user_id = parent.id
            sg_balance.type = AccountBalance.TOPUP_AMOUNT
            sg_balance.account_class = AccountBalance.PRIVATE_ACCOUNT
            sg_balance.balance = parent.sg_balance
            sg_balance.rate = sg_rate
            sg_balance.save()
            balance_changes = BalanceChangeNew.objects.filter(parent_user_id=parent.id).all()

            balance_id = normal_balance.id
            commit_list = []

            for balance_change in balance_changes:

                if balance_change.create_time.strftime('%Y-%m-%d %H:%M:%S') < '2020-02-01 00:00:00':

                    # balance_change.balance_id = normal_balance.id
                    # balance_change.save()
                    commit_list.append((normal_balance.id, balance_change.id))
                    balance_id = normal_balance.id

                else:

                    if balance_change.reason in (BalanceChangeNew.AD_HOC, BalanceChangeNew.ABSENCE_PENALTY, BalanceChangeNew.NO_SHOW_COMPENSATION):

                        '''virtualclass是新加坡小班课的话， balance id是sg_balance的id, 其他都是普通balance id'''

                        vc = VirtualclassInfo.objects.select_related('lesson__course').select_related('lesson__course__course_edition').filter(id=balance_change.reference).first()

                        if vc:

                            if vc.class_type_id == ClassType.SMALLCLASS and vc.lesson.course.course_edition.id == CourseEdition.SG and balance_change.amount in(-1, 1):

                                # balance_change.balance_id = sg_balance.id
                                # balance_change.save()
                                commit_list.append((sg_balance.id, balance_change.id))
                                balance_id = sg_balance.id
                                # continue

                    elif balance_change.reason in (BalanceChangeNew.TOP_UP, BalanceChangeNew.BONUS, BalanceChangeNew.REFERRAL_INCENTIVE, BalanceChangeNew.REFUND):

                        '''查询recharge_order, 有sg_class就是sg_balance'''

                        recharge_order = RechargeOrder.objects.filter(order_no=balance_change.reference).first()

                        if recharge_order:

                            if recharge_order.currency == 'SGD' and recharge_order.rate == 30:

                                # balance_change.balance_id = sg_balance.id
                                # balance_change.save()
                                commit_list.append((sg_balance.id, balance_change.id))
                                balance_id = sg_balance.id
                                # continue
                    else:
                        commit_list.append((normal_balance.id, balance_change.id))
                        balance_id = normal_balance.id
                sql = '''\nupdate finance_balance_change set balance_id={} where id={};\n'''.format(balance_id,
                                                                                                   balance_change.id)
                print(sql)

        #     sql = '''update finance_balance_change set balance_id=%s where id=%s'''
        #
        #     with connections['lingoace'].cursor() as cursor:
        #         try:
        #
        #             cursor.executemany(sql, commit_list)
        #             connections['lingoace'].commit()
        #         except Exception as e:
        #             print('{}'.format(e))
        #             connections['lingoace'].rollback()
        #             connections['lingoace'].close()
        #     sql = '''update finance_balance_change set balance_id={} where id={}'''.format(balance_id, balance_change.id)
        #     print(sql)
        #     # f.write(sql)
        # # f.close()
