from django.core.management.base import BaseCommand
import os
import openpyxl
from student.models import UserInfo, UserParentInfo
from finance.models import BalanceChange, AccountBalance, Transfer
from django.db.models import Q, Sum
from django.utils import timezone

'''转入转出课时'''

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file_name',
                            dest='file_name',
                            default='')

        parser.add_argument('--sheet_name',
                            dest='sheet_name',
                            default='')
        parser.add_argument('--sheet_name2',
                            dest='sheet_name2',
                            default='')

    def handle(self, *args, **kwargs):
        file_name = kwargs.get('file_name')
        sheet_name = kwargs.get('sheet_name', None)
        sheet_name2 = kwargs.get('sheet_name2', None)

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
            for cases in list(sh.rows)[1:]:
                if not cases[0].value:
                    break
                transfer_username = str(cases[0].value).strip()

                amount = float(cases[1].value)
                recipte_username = str(cases[2].value).strip()
                xg_username = str(cases[4].value).strip()
                create_time = timezone.now()

                xg_user = UserInfo.objects.filter(username=xg_username).first()

                transfer_parent = UserParentInfo.objects.filter(
                    Q(username=transfer_username) | Q(email=transfer_username) | Q(phone=transfer_username)).first()

                if not transfer_parent:
                    print('未找到转出课时用户', transfer_username)
                    continue

                recipte_parent = UserParentInfo.objects.filter(
                    Q(username=recipte_username) | Q(email=recipte_username) | Q(phone=recipte_username)).first()

                if not recipte_parent:
                    print('未找到转入课时用户', recipte_username)
                    continue

                transfer_parent_balance = AccountBalance.objects.filter(parent_user_id=transfer_parent.id, state=AccountBalance.NOT_DELETE, status=0, account_class=AccountBalance.NORMAL_ACCOUNT).values('parent_user_id').annotate(balance_sum=Sum('balance')).values('parent_user_id', 'balance_sum').first()

                # if transfer_parent_balance.get('balance_sum') < amount:
                #     print('转出账户课时余额不够', transfer_username)
                #     continue

                transfer_data = Transfer()

                transfer_data.amount = amount
                transfer_data.transfer_user_id = transfer_parent.id
                transfer_data.recipient_user_id = recipte_parent.id

                print("""insert into finance_transfer(id, amount, transfer_user_id, recipient_user_id, create_time, update_time) values({},{},{},{},'{}','{}')""".format(
                    2102, amount, transfer_parent.id, recipte_parent.id, '2020-07-17 08:10:10', '2020-07-17 08:10:10'))

                account_balance = AccountBalance()

                account_balance.balance = 0 - amount
                account_balance.type = AccountBalance.BONUS_AMOUNT
                account_balance.account_class = AccountBalance.NORMAL_ACCOUNT
                account_balance.rate = 0
                account_balance.status = 0
                account_balance.parent_user_id = transfer_parent.id

                print("""insert into accounts_balance(balance, type, account_class, rate, status, parent_user_id, state, create_time, update_time) values({},{},{},{},{},{},{},'{}','{}')""".format(
                    account_balance.balance, account_balance.type, account_balance.account_class, account_balance.rate, account_balance.status, account_balance.parent_user_id, 0, '2020-07-17 08:10:10', '2020-07-17 08:10:10'
                ))

                recipte_account_balance = AccountBalance()

                recipte_account_balance.balance = amount
                recipte_account_balance.type = AccountBalance.BONUS_AMOUNT
                recipte_account_balance.account_class = AccountBalance.NORMAL_ACCOUNT
                recipte_account_balance.rate = 0
                recipte_account_balance.status = 0
                recipte_account_balance.parent_user_id = recipte_parent.id

                print(
                    """insert into accounts_balance(balance, type, account_class, rate, status, parent_user_id, state, create_time, update_time) values({},{},{},{},{},{},{},'{}','{}')""".format(
                        recipte_account_balance.balance, recipte_account_balance.type, recipte_account_balance.account_class,
                        recipte_account_balance.rate, recipte_account_balance.status, recipte_account_balance.parent_user_id, 0,
                        '2020-07-17 08:10:10', '2020-07-17 08:10:10'
                    ))

                balance_change = BalanceChange()
                balance_change.role = BalanceChange.PARENT
                balance_change.user_id = transfer_parent.id
                balance_change.parent_user_id = transfer_parent.id
                balance_change.amount = 0-amount
                balance_change.normal_amount = 0
                balance_change.reason = BalanceChange.TRANSFER_OUT
                balance_change.reference = 2102
                balance_change.balance_id = account_balance.id

                recipte_balance_change = BalanceChange()
                balance_change.role = BalanceChange.PARENT
                recipte_balance_change.user_id = recipte_parent.id
                recipte_balance_change.parent_user_id = recipte_parent.id
                recipte_balance_change.amount = amount
                recipte_balance_change.normal_amount = 0
                recipte_balance_change.reason = BalanceChange.TRANSFER_OUT
                recipte_balance_change.reference = 2102
                recipte_balance_change.balance_id = account_balance.id

                if xg_user:
                    balance_change.xg_user_id = xg_user.id
                    recipte_balance_change.xg_user_id = xg_user.id

                print(
                    """insert into finance_balance_change(role, user_id, parent_user_id, amount, normal_amount, reason, reference, balance_id, xg_user_id, 'create_time', 'update_time') values({},{},{},{},{},{},{},{},'{}','{}')""".format(
                        balance_change.role, balance_change.user_id, balance_change.parent_user_id,
                        balance_change.amount, balance_change.normal_amount, balance_change.reason,
                        balance_change.reference, balance_change.balance_id,  balance_change.xg_user_id,
                        '2020-07-17 08:10:10', '2020-07-17 08:10:10'
                    ))

                print(
                    """insert into finance_balance_change(role, user_id, parent_user_id, amount, normal_amount, reason, reference, balance_id, xg_user_id, 'create_time', 'update_time') values({},{},{},{},{},{},{},{},'{}','{}')""".format(
                        recipte_balance_change.role, recipte_balance_change.user_id, recipte_balance_change.parent_user_id,
                        recipte_balance_change.amount, recipte_balance_change.normal_amount, recipte_balance_change.reason,
                        recipte_balance_change.reference, recipte_balance_change.balance_id, recipte_balance_change.xg_user_id,
                        '2020-07-17 08:10:10', '2020-07-17 08:10:10'
                    ))

            # sheet2 = wb['Sheet2']
            #
        if sheet_name2:
            sheet2 = wb[sheet_name2]
            self.first_course_record(sheet2)
        wb.close()