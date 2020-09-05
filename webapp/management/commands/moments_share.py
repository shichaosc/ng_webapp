from django.core.management.base import BaseCommand
import openpyxl
import os
from student.models import UserParentInfo
from django.db.models import Q
from finance.models import BalanceChange, AccountBalance as AccountBalanceNew, RechargeOrder

'''朋友圈赠课'''

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--file_name',
                            dest='file_name',
                            default='')

        parser.add_argument('--sheet_name',
                            dest='sheet_name',
                            default='')

    def handle(self, *args, **kwargs):

        file_name = kwargs.get('file_name')
        sheet_name = kwargs.get('sheet_name', None)

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        path = os.path.join(path, 'files')

        file_path = os.path.join(path, file_name)
        print(file_path)
        # 读取excle
        wb = openpyxl.load_workbook(file_path)

        # 选择sheet
        if sheet_name:
            sh = wb[sheet_name]
            # ce = sh.cell(row=1, column=1)  # 读取第一行，

            for cases in list(sh.rows)[0:]:
                parent_name = str(cases[0].value).strip()

                parent = UserParentInfo.objects.filter(Q(username=parent_name)|Q(email=parent_name)|Q(phone=parent_name)).only('id').first()

                if not parent:
                    print('未找到该用户--', parent_name)
                    continue
                recharge_count = RechargeOrder.objects.filter(parent_user_id=parent.id, status=RechargeOrder.PAID).count()
                if not recharge_count:
                    print('未充值用户--', parent_name)
                    continue
                print('已充值用户--', parent_name)
                account_balance = AccountBalanceNew()
                account_balance.balance = 0
                account_balance.type = AccountBalanceNew.BONUS_AMOUNT
                account_balance.account_class = AccountBalanceNew.NORMAL_ACCOUNT
                account_balance.rate = 0
                account_balance.status = 0
                account_balance.parent_user_id = parent.id
                account_balance.save(force_insert=True)

                balance_change = BalanceChange()
                balance_change.role = BalanceChange.PARENT
                balance_change.user_id = parent.id
                balance_change.parent_user_id = parent.id
                balance_change.amount = 1
                balance_change.normal_amount = 0
                balance_change.reason = BalanceChange.COMPENSATION
                balance_change.reference = 0
                balance_change.balance_id = account_balance.id
                balance_change.save(force_insert=True)
        wb.close()
