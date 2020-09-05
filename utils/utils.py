import datetime
import random
import string
import hashlib
import pytz
from scheduler.app_settings import EVENT_DURATION
import calendar
import uuid
import os
import requests
import json
import logging
from django.core.serializers.json import DjangoJSONEncoder, is_aware, duration_iso_string, Promise, six
import decimal
from django.utils import timezone

logger = logging.getLogger('pplingo.ng_webapp.course')

tz = pytz.timezone('Asia/Shanghai')


class DjangoJSONEncoder(DjangoJSONEncoder):
    """
        JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
        """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + '.000Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, Promise):
            return six.text_type(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)


def get_today_date():
    return datetime.date.today()


def get_few_date(day=0):
    '''
    获得今天前几天或后几天的日期
    :param day: int
    :return: date
    '''
    return get_today_date() + datetime.timedelta(days=day)


def get_few_date_time(date_time=None, day=0):
    '''
    获得当前时间前几天或后几天的时间
    :param :
        date_time datetime utc,
        day int
    :return: datetime
    '''
    if not date_time:
        date_time = datetime.datetime.now(tz=tz)
    return date_time + datetime.timedelta(days=day)


def get_day_start_end(date_time=None):
    '''
    获得传入时间那天的开始时间和结束时间
    :param date_time: datetime utc
    :return: datetime utc, datetime utv
    '''

    if not date_time:
        date_time = datetime.datetime.now(tz=tz)
    start_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 0, 0, 0, tzinfo=tz)
    end_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59, tzinfo=tz)
    return start_time, end_time


def random_str(num):
    '''
    获得随机码
    :param num: 随机码长度
    :return:
    '''
    salt = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return salt


def encrypt_passwd(passwd, salt):
    '''
    md5加密
    :param passwd:
    :param salt:
    :return:
    '''
    _passwd = passwd + salt
    return hashlib.md5(_passwd.encode("utf-8")).hexdigest()

def getNowMonth(date_day=None):
    '''
    获得本月的开始时间跟结束时间
    :return: datetime utc, datetime utc
    '''
    if not date_day:
        date_day = datetime.date.today()
    month = date_day.month
    year = date_day.year
    _, day = calendar.monthrange(year, month)  # month_day 是这个月有多少天
    # 上个月最后一天
    month_begin = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=pytz.UTC)
    month_end = datetime.datetime(year, month, day, 23, 59, 59, tzinfo=pytz.UTC)
    return month_begin, month_end

def getNowMonthBj(date_day=None):
    '''
    获得本月的开始时间跟结束时间
    :return: datetime utc, datetime utc
    '''
    if not date_day:
        date_day = datetime.date.today()
    month = date_day.month
    year = date_day.year
    _, day = calendar.monthrange(year, month)  # month_day 是这个月有多少天
    # 上个月最后一天
    month_begin = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=tz)
    month_end = datetime.datetime(year, month, day, 23, 59, 59, tzinfo=tz)
    return month_begin, month_end

def get_berfore_month_datetime(d=None):
    """
    d: date
    返回指定月份上一个月第一个天和最后一天的日期时间
    :return
    date_from: 2016-01-01 00:00:00
    date_to: 2016-01-31 23:59:59
    """
    if not d:
        d = datetime.datetime.today()
    dayscount = datetime.timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0, tzinfo=pytz.UTC)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59, tzinfo=pytz.UTC)
    return date_from, date_to


def get_attend_class_before(end_time=None):
    '''
    通过课堂的结束时间获得课堂的开始时间
    :param end_time:  datetime UTC
    :return:  datetiem UTC
    '''
    if not end_time:
        end_time = get_few_date_time()
    return end_time - datetime.timedelta(minutes=EVENT_DURATION)


def datetime_to_str(date_time):
    '''
    datetime格式化成字符串 %Y-%m-%d %H:%M:%S
    :param date_time: datetime
    :return: str
    '''
    date_time = date_time.astimezone(tz)
    return datetime.datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')


def datetime_str(date_time):
    '''
    datetime(utc时区)转换成utc字符串
    :param date_time:
    :return:
    '''
    return datetime.datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')


def get_day_start_end_utc(date_time=None):
    '''
    获得传入时间那天的开始时间和结束时间
    :param date_time: datetime utc
    :return: datetime beijing, datetime beijing
    '''
    if not date_time:
        date_time = datetime.datetime.now(tz=pytz.UTC)
    start_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 0, 0, 0, tzinfo=pytz.UTC)
    end_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59, tzinfo=pytz.UTC)
    return start_time, end_time


def datetime_utc_to_beijing(date_time):
    '''
    utc时区时间转北京时间
    :param date_time:
    :return:
    '''

    return date_time - datetime.timedelta(hours=8)


def get_file_path(instance, filename):
    """
    Function: common function to generate unique filename for all file resources, including courseware, homework etc

    Description:
        It will be called when file is uploaded and save the model. Once model is saved, file will be renamed
        with return value, and database will be updated.

    Args:
        instance (int): instance of the model.
        filename (str): original file name, including extension.

    Returns:
        str: filename with relative path
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('cw', filename)


def get_new_file_path(filename):
    """
    Function: common function to generate unique filename for all file resources, including courseware, homework etc

    Description:
        It will be called when file is uploaded and save the model. Once model is saved, file will be renamed
        with return value, and database will be updated.

    Args:
        instance (int): instance of the model.
        filename (str): original file name, including extension.

    Returns:
        str: filename with relative path
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('cw', filename)


def fetch_put_api(url, params, user_id=''):
    '''
    调用java接口
    :param url:
    :param data: dict
    :return:
    '''

    headers = {
        'content-type': 'application/json'
    }

    data = json.dumps(params, cls=DjangoJSONEncoder)

    logger.debug('url: {}, data: {}, user_id: {}'.format(url, data, user_id))

    try:
        result = requests.put(url, data=data, headers=headers)

        result = result.json()

        logger.debug('java api, url: {}, result: {}, user_id: {}'.format(url, result, user_id))

        return result

    except Exception as e:

        logger.debug('java api error, error={}'.format(e))

    return None


def fetch_delete_api(url, data, user_id=''):
    headers = {
        'content-type': 'application/json'
    }
    if data:
        data = json.dumps(data, cls=DjangoJSONEncoder)

    logger.debug('url: {}, data: {}, user_id: {}'.format(url, data, user_id))

    try:
        result = requests.delete(url, headers=headers, data=data)

        result = result.json()

        logger.debug('url: {}, result: {}, user_id: {}'.format(url, result, user_id))

        return result

    except Exception as e:

        logger.debug('java api error, error={}'.format(e))

    return None


def fetch_post_api(url, params=None, user_id=''):
    '''
    调用java接口
    :param url:
    :param data: dict
    :return:
    '''

    headers = {
        'content-type': 'application/json'
    }

    data = json.dumps(params, cls=DjangoJSONEncoder)
    # data = params
    logger.debug('url: {}, data: {}, user_id: {}'.format(url, data, user_id))
    try:
        result = requests.post(url, data=data, headers=headers)

        result = result.json()

        logger.debug('url: {}, result: {}'.format(url, result, user_id))

        return result

    except Exception as e:

        logger.debug('java api error, error={}'.format(e))

    return None


def fetch_get_api(url, params=None):
    '''
    调用java接口
    :param url:
    :param data: dict
    :return:
    '''

    headers = {
        'content-type': 'application/json'
    }

    # data = json.dumps(params, cls=DjangoJSONEncoder)
    data = params

    try:
        result = requests.get(url, data=data, headers=headers)

        result = result.json()

        # logger.debug('url: {}, result: {}'.format(url, result))

        return result

    except Exception as e:

        logger.debug('java api error, error={}'.format(e))

    return None


def utc_time_to_beijing(date_time):
    '''
    :param date_time:   utc时区的时间
    :return:   北京时区的时间
    '''
    return date_time.astimezone(tz=tz)


def get_start_end_month(year=None, month=None):

    if not year or not month:
        now_time = timezone.now().astimezone(tz=tz)
        year = now_time.year
        month = now_time.month
    year = int(year)
    month = int(month)
    _, month_day = calendar.monthrange(year, month)  # month_day 是这个月有多少天
    date_from = datetime.datetime(year, month, 1, 0, 0, 0).replace(tzinfo=tz)
    date_to = datetime.datetime(year, month, month_day, 23, 59, 59).replace(tzinfo=tz)
    return date_from, date_to
