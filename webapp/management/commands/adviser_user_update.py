from django.core.management.base import BaseCommand
from student.models import UserParentInfo
from manage.models import UserInfo
import os
import openpyxl
from webapp.utils import print_insert_table_times


class Command(BaseCommand):

    @print_insert_table_times
    def handle(self, *args, **options):

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        file_path = os.path.join(path, 'files/paidcustomers.xlsx')
        # 读取excle
        wb = openpyxl.load_workbook(file_path)

        # 选择sheet
        sh = wb['Sheet1']
        # ce = sh.cell(row=1, column=1)  # 读取第一行，第一列的数据

        for cases in list(sh.rows)[1:]:
            parent_user_id = str(cases[0].value).strip()
            adviser_username = str(cases[7].value).strip()

            user_parent_info = UserParentInfo.objects.filter(id=parent_user_id).first()

            if not user_parent_info:
                print('not found user_parent_info, id={}'.format(parent_user_id))
                continue

            adviser = UserInfo.objects.filter(username=adviser_username).first()

            if not adviser:
                print('not found adviser, username={}'.format(adviser_username))
                continue

            result = UserParentInfo.objects.filter(id=user_parent_info.id, balance=user_parent_info.balance, bonus_balance=user_parent_info.bonus_balance, sg_balance=user_parent_info.sg_balance).update(adviser_user_id=adviser.id, adviser_user_name=adviser.realname)
            if result != 1:
                print('not update from user_parent_info where id={}'.format(user_parent_info.id))
            # user_parent_info.adviser_user_id = adviser.id
            # user_parent_info.adviser_user_name = adviser.realname
            # user_parent_info.save()

