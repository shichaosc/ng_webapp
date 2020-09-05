from webapp.models import *
from finance.models import RechargeOrder, BalanceChangeNew
from django.core.management.base import BaseCommand
from student.models import UserParentInfo


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        sales_order_list = SalesOrder.objects.filter(status=SalesOrder.REFUNDED).all()

        for sale_order in sales_order_list:
            try:
                user = sale_order.buyer

                parent_user = UserParentInfo.objects.filter(username=user.username).first()
                if not parent_user:
                    print(sale_order.order_no, '未查到学生', user.username)

                recharge_order = RechargeOrder.objects.filter(order_no=sale_order.order_no).first()
                if not recharge_order:
                    recharge_order = RechargeOrder()
                    recharge_order.order_no = sale_order.order_no
                    recharge_order.status = RechargeOrder.PAID
                    recharge_order.parent_user = parent_user
                    if sale_order.package_id:
                        recharge_order.recharge_type = RechargeOrder.PACKAGE
                    if sale_order.coupon:
                        recharge_order.code = sale_order.coupon.code
                    recharge_order.recharge_amount = sale_order.point
                    recharge_order.incentive_amount = 0
                    recharge_order.total_price = sale_order.amount
                    recharge_order.origin_total_price = sale_order.amount
                    recharge_order.save_price = 0

                    recharge_order.total_amount = sale_order.point
                    recharge_order.reference = sale_order.reference

                    currency = ExchangeRate.objects.filter(currency=sale_order.currency).first()

                    recharge_order.currency_id = currency.id
                    recharge_order.currency = currency.currency
                    recharge_order.rate = currency.rate

                    recharge_order.status = RechargeOrder.PAID
                    recharge_order.create_time = sale_order.created_on
                    recharge_order.update_time = sale_order.updated_on
                    recharge_order.save()

                refund_order = RechargeOrder.objects.filter(reference=recharge_order.order_no, status=RechargeOrder.REFUND).first()

                if refund_order:
                    continue

                refund_order = RechargeOrder()
                refund_order.reference = recharge_order.order_no
                refund_order.status = RechargeOrder.REFUND
                refund_order.parent_user = recharge_order.parent_user
                if sale_order.package_id:
                    refund_order.recharge_type = RechargeOrder.PACKAGE
                if sale_order.coupon:
                    refund_order.code = sale_order.coupon.code
                refund_order.recharge_amount = sale_order.point
                refund_order.incentive_amount = 0
                refund_order.total_price = sale_order.amount
                refund_order.save_price = 0
                refund_order.origin_total_price = sale_order.amount
                refund_order.total_amount = sale_order.point
                currency = ExchangeRate.objects.filter(currency=sale_order.currency).first()
                refund_order.currency_id = currency.id
                refund_order.currency = currency.currency
                refund_order.rate = currency.rate
                refund_order.create_time = sale_order.created_on
                refund_order.update_time = sale_order.updated_on
                refund_order.save()

                # 充值的balance_change 记录
                # BalanceChangeNew.objects.filter(reference=sale_order.order_no).update(reference=recharge_order.order_no)

                # 退费的balance_change 记录

                abc_list = AccountBalanceChange.objects.filter(reference=sale_order.order_no, reason=AccountBalanceChange.REFUND).all()

                for abc in abc_list:
                    refund_balance = BalanceChangeNew()

                    refund_balance.reference = refund_order.order_no

                    refund_balance.amount = abc.amount
                    refund_balance.create_time = abc.created_on
                    refund_balance.update_time = abc.updated_on
                    refund_balance.role = BalanceChangeNew.PARENT
                    refund_balance.user_id = parent_user.id
                    refund_balance.reason = BalanceChangeNew.REFUND
                    course_adviser_student = CourseAdviserStudent.objects.filter(start_time__lte=abc.created_on,
                                                                                 student_id=abc.user_id).order_by(
                        '-start_time').first()
                    learn_manager_student = LearnManagerStudent.objects.filter(start_time__lte=abc.created_on,
                                                                               student_id=abc.user_id).order_by(
                        '-start_time').first()
                    if learn_manager_student:
                        refund_balance.xg_user_id = learn_manager_student.cms_user.id
                    if course_adviser_student:
                        refund_balance.adviser_user_id = course_adviser_student.cms_user.id

                    refund_balance.save()
            except Exception as e:
                print(e)
                print(sale_order.order_no)
