from django.core.management.base import BaseCommand
import openpyxl
import os
from student.models import UserParentInfo
from django.db.models import Q
from finance.models import BalanceChange, AccountBalance as AccountBalanceNew
from manage.models import UserInfo

'''试听课奖励发放奖励课时'''

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
                adviser_name = str(cases[0].value).strip()
                parent_name = str(cases[1].value).strip()
                create_time = cases[2].value

                adviser = UserInfo.objects.filter(username=adviser_name).first()

                parent = UserParentInfo.objects.filter(Q(username=parent_name)|Q(email=parent_name)|Q(phone=parent_name)).first()

                if not parent:
                    print('未找到该用户', adviser_name, parent_name, create_time)
                    continue

                account_balance = AccountBalanceNew()

                account_balance.balance = 0
                account_balance.type = AccountBalanceNew.BONUS_AMOUNT
                account_balance.account_class = AccountBalanceNew.NORMAL_ACCOUNT
                account_balance.rate = 0
                account_balance.status = 0
                account_balance.parent_user_id = parent.id
                account_balance.save()

                balance_change = BalanceChange()
                balance_change.role = BalanceChange.PARENT
                balance_change.user_id = parent.id
                balance_change.parent_user_id = parent.id
                balance_change.amount = 1
                balance_change.normal_amount = 0
                balance_change.reason = BalanceChange.COMPENSATION
                balance_change.reference = 0
                balance_change.balance_id = account_balance.id

                if adviser:
                    balance_change.adviser_user_id = adviser.id
                balance_change.save()

        # sheet2 = wb['Sheet2']
        #
        if sheet_name2:
            sheet2 = wb[sheet_name2]
            self.first_course_record(sheet2)
        wb.close()

    def first_course_record(self, sheet):

        for cases in list(sheet.rows)[2:]:
            adviser_name = str(cases[0].value)
            refer_name = str(cases[1].value).strip()
            parent_name = str(cases[2].value).strip()
            create_time = cases[3].value

            adviser = UserInfo.objects.filter(username=adviser_name).first()

            parent = UserParentInfo.objects.filter(Q(username=parent_name)|Q(email=parent_name)|Q(phone=parent_name)).first()

            refer = UserParentInfo.objects.filter(Q(username=refer_name)|Q(email=refer_name)|Q(phone=refer_name)).first()

            if not refer or not parent:
                print('未找到推荐人或被推荐人', adviser_name, refer_name, parent_name, create_time)
                continue

            account_balance = AccountBalanceNew()
            account_balance.parent_user_id = refer.id
            account_balance.type = AccountBalanceNew.BONUS_AMOUNT
            account_balance.account_class = AccountBalanceNew.NORMAL_ACCOUNT
            account_balance.status = 0
            account_balance.balance = 0
            account_balance.rate = 0

            account_balance.save()

            balance_change = BalanceChange()
            balance_change.role = BalanceChange.PARENT
            balance_change.user_id = parent.id
            balance_change.parent_user_id = refer.id
            balance_change.reference = 0
            balance_change.amount = 1
            balance_change.normal_amount = 0
            balance_change.reason = 19
            balance_change.balance_id = account_balance.id

            if adviser:
                balance_change.adviser_user_id = adviser.id
            balance_change.save()
