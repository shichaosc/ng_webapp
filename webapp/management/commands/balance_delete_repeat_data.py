from django.core.management.base import BaseCommand
from django.db import connections
from finance.models import BalanceChangeNew
import pytz
import functools
import time

'''
schedule_virtualclass_member  里面一节课学生有两条数据，扣款的时候会在fbc里面添加两条数据，但是扣课时是正确的， 删掉fbc重复记录
'''

def print_insert_table_times(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(func.__name__, '运行时间={}'.format(end_time-start_time))
        return result
    return wrapper


class Command(BaseCommand):

    def generate_sql(self, count, max_id, min_id, role, reason, create_time, update_time, parent_user_id, user_id, reference, amount):

        date_create_time = create_time.astimezone(pytz.UTC)
        if update_time:
            date_update_time = update_time.astimezone(pytz.UTC)
        else:
            date_update_time = None
        balance_changes = BalanceChangeNew.objects.filter(role=role, reason=reason, create_time=date_create_time, update_time=date_update_time, parent_user_id=parent_user_id, user_id=user_id, reference=reference, amount=amount).all()
        delete_balance_change_ids = []

        for i in range(len(balance_changes)):

            if i == 0:
                continue

            delete_balance_change_ids.append(str(balance_changes[i].id))
            # if balance_changes[i].create_time == balance_changes[i].update_time:
                # update_sql = '''update user_parent_info set bonus_balance=bonus_balance-{} where id={};'''.format(amount, parent_user_id)
                # print('update_sql: {}'.format(update_sql))
                # print(update_sql)
        delete_sql = '''\ndelete from finance_balance_change where id in({}) and role={} and reason={} and create_time='{}' and parent_user_id={} and user_id={} and reference='{}' and amount={};\n'''.format(
            ','.join(delete_balance_change_ids), role, reason, create_time, parent_user_id, user_id, reference, amount)
        # print('delete_sql: {}'.format(delete_sql))
        print(delete_sql)

    def delete_repeat_data(self):

        '''
        :param usernames: 所有账户不对的家长用户名列表
        :return:
        '''
        repeat_data_sql = '''SELECT
                    count( fbc.id ),
                    max( fbc.id ),
                    min( fbc.id ),
                    fbc.role,
                    fbc.reason,
                    fbc.create_time,
                    fbc.update_time,
                    fbc.parent_user_id,
                    fbc.user_id,
                    fbc.reference,
                    fbc.amount
                FROM
                    finance_balance_change fbc 
                WHERE
                    fbc.role IN ( 1, 2 ) and fbc.update_time is null
                GROUP BY 
                    fbc.create_time,
                    fbc.update_time,
                    fbc.adviser_user_id,
                    fbc.xg_user_id,
                    fbc.amount,
                    fbc.reason,
                    fbc.user_id,
                    fbc.parent_user_id,
                    fbc.reference,
                    fbc.role 
                HAVING
                    count( fbc.id ) > 1'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(repeat_data_sql)
            rows = cursor.fetchall()
            for row in rows:
                count = row[0]
                max_id = row[1]
                min_id = row[2]
                role = row[3]
                reason = row[4]
                create_time = row[5]
                update_time = row[6]
                parent_user_id = row[7]
                user_id = row[8]
                reference = row[9]
                amount = row[10]
                self.generate_sql(count, max_id, min_id, role, reason, create_time, update_time, parent_user_id,
                                 user_id, reference, amount)
            cursor.close()

    def update_parent_balance(self):


        sql = '''select fbc.parent_user_id, fbc.reference, fbc.amount*(count(*)-1) as amount, cvi.class_type_id, ce.id
                from finance_balance_change fbc 
                left join classroom_virtualclass_info cvi on cvi.id=fbc.reference
                left join course_lesson cl on cl.id=cvi.lesson_id
                left join course_info ci on ci.id=cl.course_id
                left join course_edition ce on ce.id=ci.course_edition_id
                where fbc.reason=1 and fbc.amount<>0 and fbc.update_time is null 
                group by fbc.parent_user_id, fbc.reference, fbc.amount,cvi.class_type_id, ce.id
                having count(*)>1'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                parent_user_id = row[0]
                amount = row[2]
                class_type_id = row[2]
                course_edition_id = row[3]

                if class_type_id == 2 and course_edition_id == 3:
                    '''新加坡小班课'''
                    update_balance_sql = '''update user_parent_info set sg_balance=sg_balance-{} where id={};'''.format(amount, parent_user_id)
                else:
                    update_balance_sql = '''update user_parent_info set balance=balance-{} where id={};'''.format(amount, parent_user_id)
                print(update_balance_sql)
            cursor.close()

    @print_insert_table_times
    def handle(self, *args, **options):

        # sql = '''select tmp.*, tmp.parent_balance-tmp.fbc_amount_sum as gaps from (
        #             select
        #                     distinct
        #                     upi.id,
        #                     upi.create_time,
        #                     upi.username,
        #                     upi.real_name,
        #                     (upi.balance + upi.bonus_balance + upi.sg_balance) as parent_balance,
        #                     (select sum(fbc.amount) from finance_balance_change fbc where fbc.parent_user_id=upi.id) as fbc_amount_sum
        #             -- 		((select sum(fbc.amount) from finance_balance_change fbc where fbc.parent_user_id=upi.id) - (upi.balance + upi.bonus_balance + upi.sg_balance)) as gaps
        #             from user_parent_info upi
        #             left join user_student_info usi on upi.id=usi.parent_user_id
        #             where upi.is_staff<>1 and upi.status=1 and usi.id is not null) tmp
        #             where (tmp.parent_balance-tmp.fbc_amount_sum)<>0  and tmp.create_time<'2020-01-15 00:00:00' order by tmp.create_time'''
        #
        # parent_ids = []
        # with connections['lingoace'].cursor() as cursor:
        #     cursor.execute(sql)
        #     rows = cursor.fetchall()
        #     for row in rows:
        #         parent_ids.append(row[1])
        #     cursor.close()
        self.delete_repeat_data()
        # self.update_parent_balance()

