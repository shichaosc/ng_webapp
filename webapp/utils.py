import logging
import pytz
import re
from datetime import timedelta, datetime, date
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
import dateutil.parser
from django.utils import timezone
from django.conf import settings
import hashlib
import time
import functools


logger = logging.getLogger(__name__)


def print_insert_table_times(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(func.__name__, '运行时间={}'.format(end_time-start_time))
        return result
    return wrapper


def get_monday_of_the_week (t_datetime):
    week_day = t_datetime.weekday()
    #if week_day == 6:
    #    week_day = -1
    monday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute, seconds=t_datetime.second)
    #print('monday is %s' % monday)

    return monday


def get_next_monday_of_the_week(t_datetime):
    week_day = t_datetime.weekday()
    #if week_day == 6:
    #    week_day = -1
    sunday = t_datetime - timedelta(days=week_day, hours=t_datetime.hour, minutes=t_datetime.minute, seconds=t_datetime.second) + timedelta(days=7)

    #print('sunday is %s' % sunday)

    return sunday


def get_last_sunday(t_datetime):
    week_day = t_datetime.weekday()
    if week_day == 6:
        week_day = -1
    sunday = t_datetime - timedelta(days=week_day)

    return sunday

def get_end_time(t_start, duration=60):
    return t_start + timedelta(minutes=duration)


def get_one_week_range(cur_date, t_default=None, action=None):
    # d = cur_date.astimezone(pytz.timezone('UTC'))
    # if not d:
    #     if not t_default:
    #         d_default = date.today()
    #     else:
    #         d_default = t_default.date()
    #     d = d_default.strftime('%Y-%m-%d')
    if not cur_date:
        cur_date = timezone.now()  # utc 时间 北京时间-8
    else:
        cur_date = timezone.make_aware(datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S"), timezone=pytz.utc)
    # users_tz = timezone.get_current_timezone()

    t_datetime = get_localized_datetime(cur_date)

    #logger.debug('current_date is: %s, and parsed as %s' % (d, t_datetime))

    if action:
        if action == 'previous':
            t_datetime = t_datetime - timedelta(days=7)
        elif action == 'next':
            t_datetime = t_datetime + timedelta(days=7)

    d = t_datetime.astimezone(pytz.timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')

    t_monday = get_monday_of_the_week(t_datetime)
    t_next_monday = get_next_monday_of_the_week(t_datetime)

    logger.debug('current_date is: {}, and parsed as {}; and monday is {}, and next monday is {}'.format(
        d, t_datetime, t_monday, t_next_monday))
    return d, t_monday, t_next_monday


def get_one_week_range_v2(cur_date, t_default=None, action=None):
    # d = cur_date.astimezone(pytz.timezone('UTC'))
    # if not d:
    #     if not t_default:
    #         d_default = date.today()
    #     else:
    #         d_default = t_default.date()
    #     d = d_default.strftime('%Y-%m-%d')
    users_tz = timezone.get_current_timezone()
    if not cur_date:
        cur_date = get_localized_datetime(timezone.now())
    else:
        cur_date = timezone.make_aware(datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S"), timezone=users_tz)

    t_datetime = get_localized_datetime(cur_date)

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


def get_timezone_by_name(time_zone, offset):
    """
    TODO: it isn't called yet, and it is to handle the exception of timezone name
    """
    try:
        tz = pytz.timezone(time_zone)
        return tz
    except UnknownTimeZoneError:
        return None


def get_localized_datetime(date, tz = None):
    if tz:
        users_tz = tz
    else:
        # 拿到浏览器的时区
        users_tz = timezone.get_current_timezone()

    logger.debug('timezone is {}'.format(users_tz))
    if not date:
        return None

    if type(date) is str:
        if len(date) == 10:
            try:
                t_date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return None
        else:
            t_date = dateutil.parser.parse(date)
    else:
        t_date = date

    if t_date.tzinfo is None or t_date.tzinfo.utcoffset(t_date) is None:
        return users_tz.localize(t_date, is_dst=None)
    else:
        return t_date.astimezone(users_tz)

def get_hours_in_the_week(t_time):
    return t_time.weekday() * 24 + t_time.hour + t_time.minute/60

def get_conflict_notification(conflict_sub):
    if settings.DEBUG:
        return "A time conflict exists with subscription at {}, from {} to {}, ID {}".format(
                    timezone.localtime(conflict_sub.event.start).strftime('%I:%M %p %a'),
                    timezone.localtime(conflict_sub.start_time).strftime('%Y-%m-%d'),
                    timezone.localtime(conflict_sub.end_time).strftime('%Y-%m-%d'),
                    conflict_sub.id)
    else:
        return "A time conflict exists with subscription at {}, from {} to {}".format(
                    timezone.localtime(conflict_sub.event.start).strftime('%I:%M %p %a'),
                    timezone.localtime(conflict_sub.start_time).strftime('%Y-%m-%d'),
                    timezone.localtime(conflict_sub.end_time).strftime('%Y-%m-%d'))


def get_datetime_from_request(request, param_name):

    time_zone = request.data.get('time_zone')
    #time_diff = request.GET.get('time_diff')

    tz = pytz.timezone(str(time_zone))

    return get_localized_datetime(request.data.get(param_name), tz)


def get_boolean_from_request(request, param_name):
    data = request.data.get(param_name, '')

    if data == 'True' or data == 'true' or data == '1':
        return True

    return False


def check_cancel_remaining(cancel_remaining):
    if cancel_remaining == '1':
        return True
    elif cancel_remaining == '0':
        return False
    else:
        return None


def get_datetime_to_hm(time):
    if time:
        return time.strftime("%H:%M")
    else:
        return None


def checkMobile(agent):
    """
    demo :
        @app.route('/m')
        def is_from_mobile():
            if checkMobile(request):
                return 'mobile'
            else:
                return 'pc'
    :param request:
    :return:
    """
    userAgent = agent
    # userAgent = env.get('HTTP_USER_AGENT')

    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(userAgent) != None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False


def get_calendar_publish_time(date_time, week_day, hour, minute, second):
    '''
    :param date_time: 时间  datetime类型
    :param week_day:  星期几  int
    :param hour:  小时  int
    :param minute:  分钟     int
    :param second:  秒钟     int
    :return:
    '''
    return date_time + timedelta(days=week_day, hours=hour, minutes=minute, seconds=second)


def set_password(password):
    return hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()


def user_gender(gender):
    if gender:
        if gender.lower() == 'male':
            return 1
        elif gender.lower() == 'female':
            return 2
        else:
            return 0
    else:
        return 0


def user_assessed(assessed):

    if assessed:
        return 2
    return 1


def user_type(virtualclass_type):
    if virtualclass_type == 'Tk':
        return 1
    elif virtualclass_type == 'Agaro':
        return 2
    return 1


def user_realname(first_name, last_name):

    if not first_name:
        first_name = ''

    if not last_name:
        last_name = ''
    return first_name + last_name


def course_session_status(session_status):

    if session_status == 'Active':
        return 1
    else:
        return 2


def course_ware_cwtype(type):

    PPT = 1
    IMAGE = 2
    PDF = 3
    if type.lower() == 'ppt':
        return 1
    elif type.lower() == 'image':
        return 2
    elif type.lower() == 'pdf':
        return 3


def test_question_status(status):

    if status.lower() == 'active':
        return 1
    elif status.lower() == 'archived':
        return 2


def ext_course_type(status):

    if status.lower() == 'option':
        return 2
    elif status.lower() == '':
        return 1


def reg_testquestion_detail(detail):

    pattern = re.compile(r'/.*?\.png')

    result = re.findall(pattern, detail)

    for res in result:
        relative_path = res.replace('/media/', '')
        aws_path = settings.MEDIA_URL + relative_path
        detail = detail.replace(res, aws_path)

    return detail
