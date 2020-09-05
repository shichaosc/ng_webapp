from django.core.management.base import BaseCommand
from django.db import connections
from finance.models import BalanceChange
from django.forms.models import model_to_dict

'''老师重复课时删除'''

class Command(BaseCommand):

    def handle(self, *args, **options):
        tutor_salary_repeat_sql = '''select fbc.user_id,fbc.reason,fbc.reference, count(*) from finance_balance_change fbc 
            where fbc.create_time>='2020-06-30 16:00:00' and fbc.reason in(7,8) and fbc.role=3
            group by fbc.user_id, fbc.reason, fbc.reference
             having count(*)>1'''

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(tutor_salary_repeat_sql)
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                tutor_user_id = row[0]
                reason = row[1]
                reference = row[2]
                balance_change = BalanceChange.objects.filter(user_id=tutor_user_id, reason=reason, reference=reference).first()
                print('delete fbc, id={}'.format(balance_change.id), model_to_dict(balance_change))
                balance_change.delete()
