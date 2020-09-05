from django.core.management.base import BaseCommand
from webapp.models import *
from student.models import UserParentInfo
from finance.models import BalanceChangeNew as BalanceChange


class Command(BaseCommand):

    def handle(self, *args, **options):
        compensations = AccountBalanceChange.objects.filter(reason=AccountBalanceChange.COMPENSATION).all()

        for compensation in compensations:
            user = compensation.user

            parent = UserParentInfo.objects.filter(username=user.username).first()

            if parent:
                print()
                print("insert ", compensation.id)
                balance_change = BalanceChange()
                balance_change.user_id = parent.id
                balance_change.role = UserParentInfo.PARENT
                balance_change.reason = BalanceChange.COMPENSATION
                balance_change.parent_user_id = parent.id
                balance_change.create_time = compensation.created_on
                balance_change.update_time = compensation.updated_on
                balance_change.amount = compensation.amount
                balance_change.save()
            else:
                print('not insert ', compensation.id)

