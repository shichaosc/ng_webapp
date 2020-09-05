from webapp.models import *
from student.models import UserStudentInfo
from finance.models import BalanceChangeNew
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        abcs = AccountBalanceChange.objects.filter(reason=AccountBalanceChange.FREE_TRIAL).all()

        for abc in abcs:

            user = abc.user

            user_student_info = UserStudentInfo.objects.filter(Q(real_name=user.username)|Q(parent_user__username=user.username)).select_related('parent_user').first()

            if not user_student_info:
                print('abc id: {}, username: {}'.format(abc.id, user.username))
                continue
            balance_change = BalanceChangeNew()
            balance_change.role = BalanceChangeNew.PARENT
            balance_change.reason = BalanceChangeNew.FREE_TRIAL
            balance_change.amount = abc.amount
            balance_change.user_id = user_student_info.id
            balance_change.parent_user_id = user_student_info.parent_user.id
            balance_change.reference = 1
            balance_change.normal_amount = 0
            balance_change.create_time = abc.created_on
            balance_change.update_time = abc.updated_on
            balance_change.save()
