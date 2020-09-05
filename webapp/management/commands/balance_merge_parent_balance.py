from django.core.management.base import BaseCommand
from django.db import connections
from student.models import UserParentInfo



'''
两个家长账号合并，有的banlance, bonus_balance跟sg_balance没有合并过去
'''


class Command(BaseCommand):

    def handle(self, *args, **options):

        sql = '''select 
                        supi.id as super_id,
                        supi.balance+supi.bonus_balance+supi.sg_balance as supi_balance, 
                        upi.id, 
                        upi.username, 
                        upi.balance+upi.bonus_balance+upi.sg_balance as upi_balance,
                        (select sum(amount) from finance_balance_change where parent_user_id=upi.id) as fbc_amount
                from user_student_info usi 
                right join(
                select id,username, balance, bonus_balance, sg_balance from user_parent_info where id in(
                select student_parent_user_id from user_student_info where parent_user_id<>student_parent_user_id)
                and (balance<>0 or bonus_balance<>0 or sg_balance<>0)) supi on usi.student_parent_user_id=supi.id
                left join user_parent_info upi on usi.parent_user_id=upi.id'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                student_user_parent_id = row[0]
                supi_balance = row[1]
                parent_user_id = row[2]
                upi_balance = row[4]
                fbc_amount = row[5]

                if supi_balance + upi_balance == fbc_amount:
                    student_user_parent = UserParentInfo.objects.filter(id=student_user_parent_id).first()

                    update_sql = '''update user_parent_info set balance=balance+{}, bonus_balance=bonus_balance+{}, sg_balance=sg_balance+{} where id={};'''.format(
                        student_user_parent.balance, student_user_parent.bonus_balance, student_user_parent.sg_balance, parent_user_id
                    )
                    update_student_parent_sql = '''update user_parent_info set balance=0, bonus_balance=0, sg_balance=0 where id={};'''.format(student_user_parent_id)
                    print(update_sql)
                    print(update_student_parent_sql)

            cursor.close()

