# -*- code: utf-8 -*-
import calendar
import datetime
from datetime import timedelta
import pytz
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def _get_template(container, url):
    if container == 'mobile':
        s = url.split('/')
        s[-1] = s[-1] = container + '_' + s[-1]

        url = '/'.join(s)

    return url

def get_template(request, url):

    container = request.GET.get('container', '')

    if container == '':
        container = request.session.get('container', 'web')
    else:
        request.session['container'] = container

    return _get_template(container, url)


def add_months(sourcedate,months):
    """
    在一个日期上添加月份
    :param sourcedate: 需要添加的日期
    :param months: 添加的日期, 整型
    :return: 返回计算结果
    """
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


def utc_time_to_beijing(date_time):
    '''
    :param date_time:   utc时区的时间
    :return:   北京时区的时间
    '''
    return date_time.astimezone(tz=BEIJING_TZ)


def get_month_datetime(d):
    """
    d: date
    返回指定月份上一个月第一个天和最后一天的日期时间
    :return
    date_from: 2016-01-01 00:00:00
    date_to: 2016-01-31 23:59:59
    """
    if not d:
        d = utc_time_to_beijing(timezone.now()).date()
    dayscount = timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime(dayto.year, dayto.month, 1, 0, 0, 0).replace(tzinfo=BEIJING_TZ)
    date_to = datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59).replace(tzinfo=BEIJING_TZ)
    return date_from, date_to


def get_start_end_month(year=None, month=None):

    if not year or not month:
        now_time = timezone.now().astimezone(tz=BEIJING_TZ)
        year = now_time.year
        month = now_time.month
    year = int(year)
    month = int(month)
    _, month_day = calendar.monthrange(year, month)  # month_day 是这个月有多少天
    date_from = datetime.datetime(year, month, 1, 0, 0, 0).replace(tzinfo=BEIJING_TZ)
    date_to = datetime.datetime(year, month, month_day, 23, 59, 59).replace(tzinfo=BEIJING_TZ)
    return date_from, date_to


def get_monday_of_the_week(t_datetime):
    week_day = t_datetime.weekday()
    monday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute,
                                    seconds=t_datetime.second)
    return monday


def get_next_monday_of_the_week(t_datetime):
    week_day = t_datetime.weekday()
    sunday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute,
                                    seconds=t_datetime.second) + timedelta(days=7)

    return sunday


def get_one_week_range_v2(cur_date, action=None):

    if not cur_date:
        cur_date = utc_time_to_beijing(timezone.now())
    else:
        cur_date = timezone.make_aware(datetime.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S"), timezone=BEIJING_TZ)

    t_datetime = utc_time_to_beijing(cur_date)

    if action:
        if action == 'previous':
            t_datetime = t_datetime - timedelta(days=7)
        elif action == 'next':
            t_datetime = t_datetime + timedelta(days=7)

    d = t_datetime.strftime('%Y-%m-%d %H:%M:%S')

    t_monday = get_monday_of_the_week(t_datetime)
    t_next_monday = get_next_monday_of_the_week(t_datetime)

    logger.debug('current_date is: {}, and parsed as {}; and monday is {}, and next monday is {}'.format(
        d, t_datetime, t_monday, t_next_monday))
    return d, t_monday, t_next_monday
