import logging
from datetime import timedelta

from finance.models import TutorSalary
from classroom.models import VirtualclassInfo
from tutor import utils
from finance.models import BalanceChange
import datetime
from decimal import Decimal
from common.models import ExchangeRate
from database import MysqlDataBase
from tutor.models import TutorInfo
from django.utils import timezone


logger = logging.getLogger(__name__)


def statistical_tutor_salary():

    '''只统计上个月'''
    # 查询出工资基数
    now_time = timezone.now()
    cny_rate = ExchangeRate.objects.filter(currency=ExchangeRate.default_currency, valid_end__gt=now_time, valid_start__lte=now_time).first()
    cny_exchange_rate = cny_rate.rate
    sgd_rate = ExchangeRate.objects.filter(currency='SGD', valid_end__gt=now_time, valid_start__lte=now_time).first()
    sgd_exchange_rate = sgd_rate.rate
    # 获得上个月开始结束时间
    today = datetime.date.today()
    start_time, end_time = utils.get_month_datetime(today)
    logger.debug("start_time&end_time:{}, {}".format(start_time, end_time))

    # utc时区的月初月末转成北京时间
    start_time = start_time - timedelta(hours=8)
    end_time = end_time - timedelta(hours=8)

    str_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    str_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    logger.debug("str_start_time&str_end_time:{}, {}".format(str_start_time, str_end_time))
    # 查询老师工资，这个月授课数量，这个月教的学生数量，其中授课数量是reason=7时的count(amount)
    sql = '''
        SELECT
            tt.*,
            ttt.student_num from (
            SELECT
                fbc.user_id AS user_id,
                fbc.reason AS reason,
                sum( fbc.amount ) AS sum_amount,
                count( fbc.amount ) AS count_amount 
            FROM
                finance_balance_change fbc
                LEFT JOIN classroom_virtualclass_info cvi ON cvi.id = fbc.reference 
            WHERE
                cvi.start_time >= '{}' 
                AND cvi.start_time < '{}' 
                AND fbc.reason IN ( {}, {}, {}, {} ) 
            GROUP BY
                fbc.user_id,
                fbc.reason 
            ) tt
            LEFT JOIN (
            SELECT
                uti.id AS user_id,
                count( DISTINCT svm.student_user_id ) AS student_num 
            FROM
                user_tutor_info uti
                LEFT JOIN classroom_virtualclass_info cvi ON cvi.tutor_user_id = uti.id
                right join schedule_virtualclass_member svm on svm.virtual_class_id = cvi.id
            WHERE
                cvi.STATUS = {} 
                AND cvi.start_time >= '{}' 
                AND cvi.start_time < '{}' 
            GROUP BY
                uti.id 
	    ) ttt ON tt.user_id = ttt.user_id
    '''.format(str_start_time, str_end_time,
               BalanceChange.DELIVERY,
               BalanceChange.INCENTIVE,
               BalanceChange.NO_SHOW_PENALTY,
               BalanceChange.ABSENCE_COMPENSATION,
               VirtualclassInfo.FINISH_NOMAL,
               str_start_time,
               str_end_time)
    print("-------------------------------------")
    print(sql)
    mysql_db = MysqlDataBase()
    result = mysql_db.query_sql(sql)

    insert_data = {}
    for res in result:
        user_id = res[0]
        reason = res[1]
        amount = res[2]  # 工资基数
        lesson_num = res[3]  # 上课数量
        student_num = res[4]  # 本月上课数
        data_date = end_time.strftime('%Y%m')
        # student_num = res[5]  # 本月上课数
        tutor = TutorInfo.objects.filter(id=user_id).first()
        if not tutor:
            continue
        if tutor.local_area == TutorInfo.SINGAPORE:
            rate = sgd_rate
            exchange_rate = sgd_exchange_rate
        else:
            rate = cny_rate
            exchange_rate = cny_exchange_rate
        if user_id not in insert_data.keys():
            insert_data[user_id] = {}
        if reason == BalanceChange.DELIVERY:  # 基本工资
            delivery_salary = Decimal(amount) * exchange_rate
            insert_data[user_id].update(
                delivery_salary=delivery_salary,
                lesson_num=lesson_num,
            )
        elif reason == BalanceChange.INCENTIVE:  # 奖励
            incentive_salary = Decimal(amount) * exchange_rate
            insert_data[user_id].update(incentive_salary=incentive_salary)
        elif reason == BalanceChange.ABSENCE_COMPENSATION:  # 学生缺席老师补偿
            absenc_compensation_salary = Decimal(amount) * exchange_rate
            insert_data[user_id].update(absenc_compensation_salary=absenc_compensation_salary)
        elif reason == BalanceChange.NO_SHOW_PENALTY:   # 老师缺席罚金
            no_show_salary = Decimal(amount) * exchange_rate
            insert_data[user_id].update(no_show_salary=no_show_salary)
        else:
            logger.debug('reason 无法匹配，data={}'.format(res))
        insert_data[user_id].update(data_date=data_date)
        insert_data[user_id].update(currency=rate.currency)
        if student_num:
            insert_data[user_id].update(student_num=student_num)

    for user_id, value in insert_data.items():

        # # 入库，有则更新，无则插入
        try:
            TutorSalary.objects.update_or_create(
                tutor_user_id=user_id,
                data_date=value.get('data_date', ''),
                defaults=dict(
                    lesson_num=value.get('lesson_num', 0),
                    base_salary=value.get('delivery_salary', 0),
                    incentive_salary=value.get('incentive_salary', 0),
                    student_absence_salary=value.get('absenc_compensation_salary', 0),
                    tutor_absence_salary=value.get('no_show_salary', 0),
                    student_num=value.get('student_num', 0),
                    currency=value.get('currency', 0)
                ))
            # tutor_salary.save()
        except Exception as e:
            logger.error('老师工资统计插入失败，err={}'.format(e))
            logger.error('data: user_id={}, value={}'.format(user_id, value))
