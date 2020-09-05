from webapp.models import *
from django.core.management.base import BaseCommand
from finance.models import BalanceChangeNew as BalanceChange


class Command(BaseCommand):

    def handle(self, *args, **options):

        balance_change_list = BalanceChange.objects.filter(reason__in=(BalanceChange.REFERRAL, BalanceChange.REFERRAL_INCENTIVE)).all()

        for balance_change in balance_change_list:

            if balance_change.reason == BalanceChange.REFERRAL:

                reference_balance_change = BalanceChange.objects.filter(reason=BalanceChange.TOP_UP, reference=balance_change.reference).first()

                if not reference_balance_change:
                    print(balance_change.id, balance_change.reason, balance_change.reference)
                    continue

                balance_change.user_id = reference_balance_change.parent_user_id if reference_balance_change.parent_user_id else reference_balance_change.user_id
                balance_change.save()

            elif balance_change.reason == BalanceChange.REFERRAL_INCENTIVE:

                reference_balance_change = BalanceChange.objects.filter(reason=BalanceChange.REFERRAL, reference=balance_change.reference).first()

                if not reference_balance_change:
                    print(balance_change.id, balance_change.reason, balance_change.reference)
                    continue

                balance_change.user_id = reference_balance_change.parent_user_id if reference_balance_change.parent_user_id else reference_balance_change.user_id
                balance_change.save()

