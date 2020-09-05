from django.core.management.base import BaseCommand
from django.db import connections
from finance.models import BalanceChangeNew
import pytz


'''
 一个家长两个以上孩子一起上课， 只扣一个孩子的课时， 两个孩子上完课后会发送试听完成奖励， 只增加一节, 目前发现reason in(1, 19)
'''


class Command(BaseCommand):

    def update_parent_balance(self):

        sql = '''select fbc.parent_user_id, fbc.reference, fbc.amount*(count(*)-1) as amount, cvi.class_type_id, ce.id
                from finance_balance_change fbc 
                left join classroom_virtualclass_info cvi on cvi.id=fbc.reference
                left join course_lesson cl on cl.id=cvi.lesson_id
                left join course_info ci on ci.id=cl.course_id
                left join course_edition ce on ce.id=ci.course_edition_id
                where fbc.reason in(1,19) and fbc.amount<>0 and fbc.update_time is null 
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
                    update_balance_sql = '''update user_parent_info set sg_balance=sg_balance+{} where id={};'''.format(amount, parent_user_id)
                else:
                    update_balance_sql = '''update user_parent_info set balance=balance+{} where id={};'''.format(amount, parent_user_id)
                print(update_balance_sql)
            cursor.close()

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

        parent_ids = []
        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                parent_ids.append(row[1])
            cursor.close()
        # self.delete_repeat_data()
        self.update_parent_balance()

