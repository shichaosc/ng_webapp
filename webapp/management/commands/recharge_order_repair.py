from django.core.management.base import BaseCommand
import os
import openpyxl
from finance.models import RechargeOrder, Payment
from student.models import UserParentInfo
from django.db.models import Q
from django.utils import timezone
from django.db import transaction

'''7.30 印尼订单修复'''

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
        now_time = timezone.now()
        if not sheet_name:
            print('not found sheet: {}'.format(sheet_name))
            return
        # try:
        wb = openpyxl.load_workbook(file_path)
        sh = wb[sheet_name]
        for cases in list(sh.rows)[2:]:
            try:
                topup_date = cases[1].value
                parent_user_name = str(cases[2].value).strip()
                currency = str(cases[3].value).strip().upper()
                price = cases[4].value
                amount = cases[5].value
                topup_amount = cases[6].value
                code = cases[7].value
                payment_method = cases[8].value
                reference = cases[9].value
                remark = cases[10].value
                if remark:
                    distinct = remark * 100
                else:
                    distinct = None
                parent_user = UserParentInfo.objects.filter(Q(username=parent_user_name)|Q(email=parent_user_name)|Q(phone=parent_user_name)).first()

                if not parent_user:
                    print('not found user: {}'.format(parent_user_name))
                    continue
                recharge_order = RechargeOrder.objects.filter(parent_user_id=parent_user.id,
                                                              reference=reference,
                                                              code=code,
                                                              status=RechargeOrder.PAID,
                                                              total_price=topup_amount,
                                                              recharge_amount=amount).last()
                if not recharge_order:
                    print(topup_date, parent_user_name, currency, price, amount, topup_amount, code, payment_method,
                          reference, remark)
                    continue
                # if recharge_order.reference:
                #     print(topup_date, parent_user_name, currency, price, amount, topup_amount, code, payment_method,
                #           reference, remark, '没有问题')
                #     continue
                with transaction.atomic():
                    recharge_order.create_time = topup_date
                    recharge_order.update_time = topup_date
                    recharge_order.save(update_fields=['create_time', 'update_time'])

                    payment = Payment.objects.filter(order_id=recharge_order.id).first()
                    payment.reference = payment_method
                    payment.success_time = recharge_order.create_time
                    payment.save(update_fields=['reference', 'success_time'])
            except Exception as e:
                print(e)
                print('{} error'.format(cases[0].value))
        wb.close()


