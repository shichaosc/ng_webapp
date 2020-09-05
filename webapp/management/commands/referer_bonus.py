from django.core.management.base import BaseCommand
from webapp.models import *
from student.models import UserParentInfo
from finance.models import BalanceChangeNew as BalanceChange


start_id = 1000000000000000
end_id = 10000000000000000


class Command(BaseCommand):

    '''学生推荐人奖励'''

    def has_referer_bonus(self, user: User):

        '''判断有没有发推荐人奖励'''

        try:
            referrer = UserReferrer.objects.get(user=user)
        except UserReferrer.DoesNotExist:
            return None
        sale_orders = SalesOrder.objects.filter(buyer=user, status=SalesOrder.PAID).all()
        sale_order_list = []
        for sale_order in sale_orders:
            sale_order_list.append(sale_order.order_no)

        account_balance_change = AccountBalanceChange.objects.filter(user=referrer.referrer,
                                                                     reason=AccountBalanceChange.REFERRAL,
                                                                     reference__in=sale_order_list).first()
        if account_balance_change:
            return account_balance_change
        return None

    def has_referral_incentive(self, parent_info: UserParentInfo):

        '''判断是否有 REFERRAL_INCENTIVE reason'''

        abc = BalanceChange.objects.filter(user_id=parent_info.id, reason=BalanceChange.REFERRAL_INCENTIVE).first()
        if abc:
            return True
        return False

    def handle(self, *args, **options):

        users = User.objects.all()

        for user in users:

            parent_info = UserParentInfo.objects.filter(username=user.username).first()

            account_balance_change = self.has_referer_bonus(user)
            if not account_balance_change:
                continue

            has_incentive = self.has_referral_incentive(parent_info)
            if has_incentive:
                continue
            print(parent_info.id, account_balance_change.reference)
            balance_change = BalanceChange.objects.filter(reference=account_balance_change.reference,
                                                          reason=BalanceChange.BONUS,
                                                          user_id=parent_info.id,
                                                          amount=account_balance_change.amount).order_by('amount').first()

            if not balance_change:
                print(BalanceChange.objects.filter(reference=account_balance_change.reference,
                                                          reason=BalanceChange.BONUS,
                                                          user_id=parent_info.id).order_by('amount').all().query)
                continue
            balance_change.reason = BalanceChange.REFERRAL_INCENTIVE
            print('balance_change_id', balance_change.id)
            balance_change.save()
