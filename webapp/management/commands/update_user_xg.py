from django.core.management.base import BaseCommand
from student.models import UserParentInfo
import openpyxl
import os
from manage.models import UserInfo


class Command(BaseCommand):

    def handle(self, *args, **options):

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        file_path = os.path.join(path, 'files/修改学管.xlsx')
        # 读取excle
        wb = openpyxl.load_workbook(file_path)

        # 选择sheet
        sh = wb['Sheet1']
        # ce = sh.cell(row=1, column=1)  # 读取第一行，第一列的数据

        for cases in list(sh.rows)[1:]:
            parent_user_id = str(cases[0].value).strip()
            xg_realname = str(cases[4].value).strip()

            user_parent_info = UserParentInfo.objects.filter(id=parent_user_id).first()

            if not user_parent_info:
                print('not found user_parent_info, id={}'.format(parent_user_id))
                continue

            xg = UserInfo.objects.filter(realname=xg_realname).first()

            if not xg:
                print('not found xg, realname={}'.format(xg_realname))
                continue

            result = UserParentInfo.objects.filter(id=user_parent_info.id, balance=user_parent_info.balance,
                                                   bonus_balance=user_parent_info.bonus_balance,
                                                   sg_balance=user_parent_info.sg_balance).update(
                xg_user_id=xg.id, xg_user_name=xg.realname)
            if result != 1:
                print('not update from user_parent_info where id={}'.format(user_parent_info.id))
            # user_parent_info.adviser_user_id = adviser.id
            # user_parent_info.adviser_user_name = adviser.realname
            # user_parent_info.save()


