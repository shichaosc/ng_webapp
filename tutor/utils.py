from django.utils import timezone as tz
from datetime import timezone, datetime, timedelta
import pytz


def deal_params_id(params_id):
    weekdays = []
    timeperiods = []
    for param_id in params_id:
        if 0 <= int(param_id) <= 6:
            weekdays.append(int(param_id))
        elif int(param_id) == 7:
            timeperiods.append(6)
        elif int(param_id) == 8:
            timeperiods.append(12)
        elif int(param_id) == 9:
            timeperiods.append(18)
    return weekdays, timeperiods


def deal_params_id_v2(params_id):
    weekdays = []
    timeperiods = []
    for param_id in params_id:
        if 0 <= int(param_id) <= 6:
            weekdays.append(str(param_id))
        elif int(param_id) == 7:
            timeperiods.append('06:00-12:00')
        elif int(param_id) == 8:
            timeperiods.append('12:00-18:00')
        elif int(param_id) == 9:
            timeperiods.append('18:00-24:00')
    return weekdays, timeperiods


def strdate_to_utcdate(strdate):
    """
    把一个"%Y%m%d%H"格式的时间str转换成UTC时间
    :param strdate:
    :return:
    """
    try:
        current_date = datetime.strptime(strdate, "%Y%m%d%H")
    except:
        return None
    current_date = tz.make_aware(current_date)
    cst_tz = timezone(timedelta(hours=0))
    return current_date.astimezone(cst_tz)


def get_monday_of_the_week(t_datetime):
    week_day = t_datetime.weekday()
    # if week_day == 6:
    #    week_day = -1
    monday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute,
                                    seconds=t_datetime.second)
    # print('monday is %s' % monday)

    return monday


def get_next_monday_of_the_week(t_datetime):
    week_day = t_datetime.weekday()
    # if week_day == 6:
    #    week_day = -1
    sunday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute,
                                    seconds=t_datetime.second) + timedelta(days=7)

    # print('sunday is %s' % sunday)

    return sunday


def get_user_one_week_range(cur_date, timedif):
    cst_tz = timezone(timedelta(hours=timedif))
    cur_date = cur_date.astimezone(cst_tz)

    t_monday = get_monday_of_the_week(cur_date)
    t_next_monday = get_next_monday_of_the_week(cur_date)

    return t_monday, t_next_monday


def get_month_datetime(d):
    """
    d: date
    返回指定月份上一个月第一个天和最后一天的日期时间
    :return
    date_from: 2016-01-01 00:00:00
    date_to: 2016-01-31 23:59:59
    """
    if not d:
        d = datetime.today()
    dayscount = timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime(dayto.year, dayto.month, 1, 0, 0, 0).replace(tzinfo=pytz.utc)
    date_to = datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59).replace(tzinfo=pytz.utc)
    return date_from, date_to
