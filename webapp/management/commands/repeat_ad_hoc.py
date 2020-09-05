from django.core.management.base import BaseCommand
import os
import openpyxl
from scheduler.models import ScheduleVirtualclassMember, StudentTimetable
from finance.models import BalanceChange, AccountBalance
from django.db.models import F, Sum
from student.models import UserStudentInfo


class Command(BaseCommand):

    '''学生重复扣课时补偿'''

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
            before_virtual_class_id = ""
            for cases in list(sh.rows)[1:]:
                fbc_id = str(cases[1].value).strip()
                virtualclass_id = str(cases[2].value).strip()
                sid = str(cases[3].value).strip()
                amount = str(cases[7].value).strip()
                if before_virtual_class_id == virtualclass_id + sid:
                    print("该virtual class已处理", cases[0].value)
                    before_virtual_class_id = None
                    continue
                before_virtual_class_id = virtualclass_id + sid
                virtual_class_id = virtualclass_id.split('_')[1]
                student_user_id = sid.split('_')[1]
                user_student_info = UserStudentInfo.objects.filter(id=student_user_id).first()
                virtual_class_members = ScheduleVirtualclassMember.objects.filter(virtual_class_id=virtual_class_id, student_user_id=student_user_id).all()
                fbcs = BalanceChange.objects.filter(reference=virtual_class_id, user_id=student_user_id, reason=BalanceChange.AD_HOC).all()
                if len(fbcs) < 2:
                    print('不符合重复扣学生课时的标准', cases[0].value)
                    continue

                parent_balances = AccountBalance.objects.filter(parent_user_id=user_student_info.parent_user_id).annotate(sum_balance=Sum('balance')).values('parent_user_id', 'sum_balance')
                parent_fbc = BalanceChange.objects.filter(parent_user_id=user_student_info.parent_user_id).annotate(sum_fbc=Sum('amount')).values('parent_user_id', 'sum_fbc')
                if len(virtual_class_members) > 1:
                    right_student_timetable_id = None
                    for virtual_class_member in virtual_class_members:

                        if right_student_timetable_id:
                            ScheduleVirtualclassMember.objects.filter(id=virtual_class_member.id).delete()
                            print("删除数据，virtula_class_id:{}, virtual_class_member_id:{}".format(virtual_class_id, virtual_class_member.id), cases[0].value)
                            break
                        '''判断schedule_student_time状态是否正确'''
                        student_timetable = StudentTimetable.objects.filter(id=virtual_class_member.student_timetable_id).first()
                        if student_timetable and student_timetable.status == StudentTimetable.SUCCESS_APPOINTMENT:
                            right_student_timetable_id = student_timetable.id
                            continue
                        else:
                            ScheduleVirtualclassMember.objects.filter(id=virtual_class_member.id).delete()
                            print("删除数据，virtula_class_id:{}, virtual_class_member_id:{}".format(virtual_class_id, virtual_class_member.id), cases[0].value)
                            break
                balance_change_id = fbc_id.split('_')[1]
                balance_change = BalanceChange.objects.filter(id=balance_change_id).first()
                if parent_fbc.get('sum_fbc') < parent_balances.get('sum_balance'):
                    print('学生fbc比学生课时少，不操作学生账户余额， parent_user_id={}, sum_balance={}, sum_fbc={}'.format(user_student_info.parent_user_id, parent_balances.get('sum_balance'), parent_fbc.get('sum_fbc')))
                else:
                    acocunt_balance = AccountBalance.objects.filter(id=balance_change.balance_id).first()
                    acocunt_balance.balance = F('balance') - balance_change.amount
                    acocunt_balance.save(update_fields=['balance', 'update_time'])
                balance_change.delete()
        wb.close()