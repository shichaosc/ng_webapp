from django.core.management.base import BaseCommand
import os
import openpyxl
from finance.models import RechargeOrder, BalanceChange, AccountBalance, Payment
from student.models import UserParentInfo
from django.db.models import Q
from common.models import ExchangeRate
from django.utils import timezone
from django.db import transaction

'''添加印尼订单'''

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
                print(cases[0].value)
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

                exchange_rate = ExchangeRate.objects.filter(currency=currency, valid_end__gt=now_time, valid_start__lte=now_time).first()

                if not exchange_rate:
                    print('not found currency: {}'.format(currency))
                    continue
                parent_user = UserParentInfo.objects.filter(Q(username=parent_user_name)|Q(email=parent_user_name)|Q(phone=parent_user_name)).first()

                if not parent_user:
                    print('not found user: {}'.format(parent_user_name))
                    continue
                with transaction.atomic():
                    recharge_order = RechargeOrder()
                    recharge_order.create_time = topup_date
                    recharge_order.update_time = topup_date
                    recharge_order.parent_user_id = parent_user.id
                    recharge_order.recharge_type = RechargeOrder.PACKAGE
                    recharge_order.code = code
                    recharge_order.recharge_amount = amount
                    recharge_order.incentive_amount = 0
                    recharge_order.total_amount = amount
                    recharge_order.currency_id = exchange_rate.id
                    recharge_order.currency = exchange_rate.currency
                    recharge_order.rate = price
                    recharge_order.origin_total_price = price * amount
                    recharge_order.save_price = price * amount - topup_amount
                    recharge_order.discount = distinct
                    recharge_order.total_price = topup_amount
                    recharge_order.reference = reference
                    recharge_order.status = RechargeOrder.PAID

                    before_recharge_order = RechargeOrder.objects.filter(parent_user_id=parent_user.id, status=1).first()
                    if before_recharge_order:
                        recharge_order.first_recharge = RechargeOrder.NOT_FIRST_RECHARGE
                    else:
                        recharge_order.first_recharge = RechargeOrder.FIRST_RECHARGE
                    recharge_order.pay_type = RechargeOrder.CARD
                    recharge_order.save()

                    account_balance = AccountBalance()
                    account_balance.parent_user_id = parent_user.id
                    account_balance.type = AccountBalance.TOPUP_AMOUNT
                    account_balance.account_class = AccountBalance.PRIVATE_ACCOUNT
                    account_balance.rate = recharge_order.total_price/recharge_order.origin_total_price
                    account_balance.balance = 0
                    account_balance.status = 0
                    account_balance.save()

                    balance_change = BalanceChange()
                    balance_change.role = BalanceChange.PARENT
                    balance_change.reason = BalanceChange.TOP_UP
                    balance_change.user_id = parent_user.id
                    balance_change.amount = recharge_order.total_amount
                    balance_change.normal_amount = 0
                    balance_change.reference = recharge_order.order_no
                    balance_change.parent_user_id = parent_user.id
                    if parent_user.adviser_user_id:
                        balance_change.adviser_user_id = parent_user.adviser_user_id
                    if parent_user.xg_user_id:
                        balance_change.xg_user_id = parent_user.xg_user_id
                    balance_change.balance_id = account_balance.id
                    balance_change.save()

                    payment = Payment()

                    payment.order_id = recharge_order.id
                    payment.amount = recharge_order.total_price
                    payment.reference = payment_method
                    payment.type = recharge_order.pay_type
                    payment.status = 1
                    payment.channel = 'stripe'
                    payment.success_time = recharge_order.create_time
                    payment.save()
            except Exception as e:
                print(e)
                print('{} error'.format(cases[0].value))
        # except Exception as e:
        #     print(e)
        # finally:
        wb.close()
