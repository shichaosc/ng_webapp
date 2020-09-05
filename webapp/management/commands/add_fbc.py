from django.core.management.base import BaseCommand
from course.models import CourseLesson, CourseUnit, CourseEdition, CourseInfo
from django.db import connections
from finance.models import RechargeOrder, BalanceChange


class Command(BaseCommand):

    def format_insert_fbc_sql(self, *args):
        insert_fbc_sql = '''insert into finance_balance_change
                        (user_id, parent_user_id, reason, amount, reference, adviser_user_id, xg_user_id, create_time, role) 
                        values({},{},{},{},'{}',{},{},'{}', {});'''.format(*args)
        print(insert_fbc_sql)

    def format_update_balance_sql(self, amount, parent_user_id):

        update_balance_sql = '''update user_parent_info set balance=balance+{} where id={};'''.format(amount, parent_user_id)
        print(update_balance_sql)

    def format_update_sg_balance_sql(self, amount, parent_user_id):

        update_balance_sql = '''update user_parent_info set balance=sg_balance+{} where id={};'''.format(amount,
                                                                                                     parent_user_id)
        print(update_balance_sql)

    def handle(self, *args, **kwargs):

        no_balance_order_sql = '''select fro.id from finance_recharge_order fro 
                                    left join finance_balance_change fbc on fbc.reference=fro.order_no
                                    where fro.status=1 and fbc.id is null'''

        no_balance_order_ids = []
        with connections['lingoace'].cursor() as cursor:
            cursor.execute(no_balance_order_sql)
            rows = cursor.fetchall()
            for row in rows:
                no_balance_order_ids.append(row[0])
            cursor.close()

        recharge_orders = RechargeOrder.objects.filter(id__in=no_balance_order_ids).select_related('parent_user').all()

        for recharge_order in recharge_orders:

            recharge_order.incentive_amount = recharge_order.incentive_amount if recharge_order.incentive_amount else 0
            recharge_order.recharge_amount = recharge_order.recharge_amount if recharge_order.recharge_amount else 0
            recharge_order.referrer_incentive_amount = recharge_order.referrer_incentive_amount if recharge_order.referrer_incentive_amount else 0

            if recharge_order.recharge_amount:
                self.format_insert_fbc_sql(
                    recharge_order.parent_user_id,
                    recharge_order.parent_user_id,
                    BalanceChange.TOP_UP,
                    recharge_order.recharge_amount,
                    recharge_order.order_no,
                    recharge_order.parent_user.adviser_user_id if recharge_order.parent_user.adviser_user_id else 'null',
                    recharge_order.parent_user.xg_user_id if recharge_order.parent_user.xg_user_id else 'null',
                    recharge_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    BalanceChange.PARENT)

            if recharge_order.incentive_amount:
                self.format_insert_fbc_sql(
                    recharge_order.parent_user_id,
                    recharge_order.parent_user_id,
                    BalanceChange.BONUS,
                    recharge_order.incentive_amount,
                    recharge_order.order_no,
                    recharge_order.parent_user.adviser_user_id if recharge_order.parent_user.adviser_user_id else 'null',
                    recharge_order.parent_user.xg_user_id if recharge_order.parent_user.xg_user_id else 'null',
                    recharge_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    BalanceChange.PARENT)

            if recharge_order.referrer_incentive_amount:

                if recharge_order.referrer_user_id:
                    self.format_insert_fbc_sql(
                        recharge_order.parent_user_id,
                        recharge_order.referrer_user_id,
                        BalanceChange.REFERRAL,
                        recharge_order.referrer_incentive_amount,
                        recharge_order.order_no,
                        recharge_order.parent_user.adviser_user_id if recharge_order.parent_user.adviser_user_id else 'null',
                        recharge_order.parent_user.xg_user_id if recharge_order.parent_user.xg_user_id else 'null',
                        recharge_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                        BalanceChange.PARENT)

                    self.format_update_balance_sql(recharge_order.referrer_incentive_amount, recharge_order.referrer_user_id)

            if recharge_order.currency == 'SGD' and recharge_order.rate == 30:
                self.format_update_sg_balance_sql(recharge_order.recharge_amount+recharge_order.incentive_amount, recharge_order.parent_user_id)

            else:
                self.format_update_balance_sql(recharge_order.recharge_amount+recharge_order.incentive_amount, recharge_order.parent_user_id)


