from django.core.management.base import BaseCommand
from student.models import UserParentInfo, UserStudentInfo
from finance.models import RechargeOrder, AccountBalance, BalanceChange
from django.db.models import Q
import logging
from django.db import connection

logger = logging.getLogger('pplingo.ng_webapp.scripts')
'''
合并账户
参数： parent_name 家长用户名
      merged_parent_name  被合并的家长用户名
账户合并规则：
1. 修改finance_recharge_order表的parent_user_id， 所有的merged_parent_name对应的parent_user_id改为parent_name对应的parent_user_id
2. 修改accounts_balance表的parent_user_id, 同上
2. 修改把finance_balance_change表的parent_user_id, 同上
3. 修改user_student_info 的parent_user_id,  同上
4. 把merged_parent_name的家长账号禁掉
'''


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--parent_name',
                            dest='parent_name',
                            default='')

        parser.add_argument('--merged_parent_name',
                            dest='merged_parent_name',
                            default='')

    def handle(self, *args, **kwargs):

        parent_name = kwargs.get('parent_name')
        merged_parent_name = kwargs.get('merged_parent_name')

        parent_info = UserParentInfo.objects.filter(
            Q(username=parent_name) | Q(email=parent_name) | Q(phone=parent_name)).first()
        if not parent_info:
            logger.debug('not found parent user where username={}'.format(parent_name))
            return
        merged_parent_info = UserParentInfo.objects.filter(
            Q(username=merged_parent_name) | Q(email=merged_parent_name) | Q(phone=merged_parent_name)).first()
        if not merged_parent_info:
            logger.debug('not found merged parent user where username={}'.format(merged_parent_name))
            return
        recharge_orders = RechargeOrder.objects.filter(parent_user_id=merged_parent_info.id).all()
        for recharge_order in recharge_orders:
            recharge_order.parent_user_id = parent_info.id
            recharge_order.save(force_update=True, update_fields=['parent_user_id', 'update_time'])
        account_balances = AccountBalance.objects.filter(parent_user_id=merged_parent_info.id).all()
        for account_balance in account_balances:
            account_balance.parent_user_id = parent_info.id
            account_balance.save(force_update=True, update_fields=['parent_user_id', 'update_time'])
        balance_changes = BalanceChange.objects.filter(parent_user_id=merged_parent_info.id).all()
        for balance_change in balance_changes:
            balance_change.parent_user_id = parent_info.id
            balance_change.save(force_update=True, update_fields=['parent_user_id', 'update_time'])
        user_student_infos = UserStudentInfo.objects.filter(parent_user_id=merged_parent_info.id).all()
        for user_student_info in user_student_infos:
            user_student_info.parent_user_id = parent_info.id
            user_student_info.save(force_update=True, update_fields=['parent_user_id', 'update_time'])
        merged_parent_info.status = UserParentInfo.FORBIDDEN
        merged_parent_info.save()

        logger.debug('parent_name {} and merged_parent_name merge {} success'.format(parent_name, merged_parent_name))
        print(connection.queries)