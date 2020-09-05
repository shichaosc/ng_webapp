from django.core.management.base import BaseCommand
from webapp.models import *
from student.models import UserParentInfo
from finance.models import BalanceChangeNew as BalanceChange, Transfer as NewTransfer


start_id = 1000000000000000
end_id = 10000000000000000


class Command(BaseCommand):

    '''插入学生转课时记录， 插入学生的推荐人'''

    def handle(self, *args, **options):
        transfer_infos = Transfer.objects.all()
        NewTransfer.objects.all().delete()

        for transfer_info in transfer_infos:

            transfer_parent = UserParentInfo.objects.filter(username=transfer_info.transfer_user.username).first()

            if not transfer_parent:
                continue
            recipient_parent = UserParentInfo.objects.filter(username=transfer_info.recipient.username).first()

            if not recipient_parent:
                continue
            transfer = NewTransfer()
            transfer.id = transfer_info.id
            transfer.transfer_user_id = transfer_parent.id
            transfer.recipient_user_id = recipient_parent.id
            transfer.amount = transfer_info.amount
            transfer.save()

        abc_list = AccountBalanceChange.objects.filter(reason__in=(AccountBalanceChange.TRANSFER_IN, AccountBalanceChange.TRANSFER_OUT)).all()
        BalanceChange.objects.filter(reason__in=(BalanceChange.TRANSFER_IN, BalanceChange.TRANSFER_OUT)).delete()
        for abc in abc_list:
            parent = UserParentInfo.objects.filter(username=abc.user.username).first()
            if not parent:
                print('user not exist', abc.id, abc.user_id, abc.user.username)
                continue

            bc = BalanceChange()
            bc.user_id = parent.id
            bc.reason = abc.reason
            bc.reference = abc.reference
            bc.amount = abc.amount
            bc.role = BalanceChange.PARENT
            bc.create_time = abc.created_on
            bc.update_time = abc.updated_on
            bc.save()

        # students = User.objects.all()
        #
        # for student in students:
        #     referer = UserReferrer.objects.filter(user=student).first()
        #     if not referer:
        #         continue
        #     referer_parent = UserParentInfo.objects.filter(username=referer.referrer.username).first()
        #     if not referer_parent:
        #         continue
        #     parent = UserParentInfo.objects.filter(username=student.username).first()
        #     if not parent:
        #         continue
        #     parent.referrer_user_id = referer_parent.id
        #     parent.referrer_user_name = referer_parent.username
        #
        #     parent.save()
