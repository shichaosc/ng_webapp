from django.core.management.base import BaseCommand
from classroom.models import VirtualclassInfo, ClassType, ClassInfo, ClassMember
from scheduler.models import TutorTimetable, StudentTimetable, ScheduleVirtualclassMember
from tutor.models import TutorInfo
from student.models import UserStudentInfo
from course.models import CourseLesson, CourseInfo
import requests
import logging
from django.db.models import Q
import json
import pytz
import datetime
from course.utils import get_next_lesson
import random
import time

logger = logging.getLogger('pplingo.ng_webapp.scripts')
'''
修补20, 21号丢失的上课数据
1. 从拓课取到20，21号所有的数据
2. 跟业务库数据对比，没有的数据插入，有的数据判断tk_class_id
'''

authkey = 'ex5lZksGvEmoeC1m'
startdate = 1597852800
enddate = 1598025600

def create_id():
    return random.randint(1000000000000000, 8999999999999999)

def get_user_student_infos(logininfo_result):
    user_student_info_list = []
    for lr in logininfo_result:
        user_role = lr.get('userroleid')
        student_user_id = None
        if user_role == '2':  # 学员
            try:
                student_user_id = int(lr.get('userid'))
            except Exception as e:
                pass
            student_user_name = lr.get('username')
            if student_user_id:
                user_student_info = UserStudentInfo.objects.filter(id=student_user_id).first()
            else:
                user_student_infos = UserStudentInfo.objects.filter(real_name=student_user_name).all()
                if len(user_student_infos) == 1:
                    user_student_info = user_student_infos[0]
                else:
                    return []
            if not user_student_info:
                return []
            user_student_info_list.append(user_student_info)
    return user_student_info_list

def get_class_info(student_user_ids):

    '''查询学生所在的班级id, 只有一个符合的班级才会返回，不然返回None'''

    class_infos = ClassInfo.objects.filter(class_member__student_user_id__in=student_user_ids).all()
    class_field = []
    for class_info in class_infos:
        if class_field is None:
            class_field = class_info
        class_members = ClassMember.objects.filter(class_field_id=class_info.id).all().values_list('student_user_id')
        class_member_ids = [class_member[0] for class_member in class_members]
        for student_user_id in student_user_ids:
            if student_user_id not in class_member_ids:
                break
        class_field.append(class_info)

    if len(class_field) > 1:
        return None
    elif len(class_field) == 1:
        return class_field[0]
    else:
        return None

def get_tk_room_type(serial):

    '''获取房间类型'''
    params = {
        "key": authkey,
        "serial": serial
    }

    url = "http://global.talk-cloud.net/WebAPI/getserialalldata"
    try:
        result = requests.post(url, data=params)
        result = result.json()  # 0 是老师， 2是学员
        logininfo = result.get('roomtype', 0)
        return logininfo
    except Exception as e:
        print('获取房间类型失败, err={}'.format(e))
    return 0

def get_virtualclass_info(tk_class_id, start_time):
    vc = VirtualclassInfo.objects.filter(tk_class_id=tk_class_id).first()
    return vc

def get_user_tutor_info(logininfo_result):
    tutor_user_id = None
    tutor_user_name = None
    for lr in logininfo_result:
        user_role = lr.get('userroleid')
        if user_role == '0':  # 老师
            try:
                tutor_user_id = int(lr.get('userid'))
                tutor_user_name = lr.get('username')
                break
            except:
                tutor_user_name = lr.get('username')
    user_tutor_info = TutorInfo.objects.filter(
        Q(id=tutor_user_id) | Q(username=tutor_user_name) | Q(email=tutor_user_name) | Q(phone=tutor_user_name)).first()
    if not user_tutor_info:
        user_tutor_infos = TutorInfo.objects.filter(Q(identity_name=tutor_user_name)|Q(real_name=tutor_user_name)).all()
        if len(user_tutor_infos) == 1:
            return user_tutor_infos[0]
        else:
            return None
    return user_tutor_info

def get_tutor_enter_leave_time(logininfo_result):
    enter_time = None
    leave_time = None
    for lr in logininfo_result:
        user_role = lr.get('userroleid')
        if user_role == '0':  # 老师
            enter_time = lr.get('entertime')
            leave_time = lr.get('outtime')
            enter_time = datetime.datetime.strptime(enter_time, '%Y-%m-%d %H:%M:%S').astimezone(tz=pytz.UTC)
            enter_time = enter_time - datetime.timedelta(hours=8)
            leave_time = datetime.datetime.strptime(leave_time, '%Y-%m-%d %H:%M:%S').astimezone(tz=pytz.UTC)
            leave_time = leave_time - datetime.timedelta(hours=8)
    return enter_time, leave_time


def get_student_logininfo(vc):

    tk_logininfo = getlogininfo(vc.tk_class_id)

    login_info_dict = {}  # 构建成student_id: {}这种格式的数据

    for info in tk_logininfo:
        if info.get('userroleid') == '2':  # 学生
            try:
                userid = int(info.get('userid'))
            except:
                username = info.get('username')
                user_student_info = UserStudentInfo.objects.filter(real_name=username).first()
                if user_student_info:
                    userid = user_student_info.id
                else:
                    continue
            if userid in login_info_dict:
                login_info_dict[userid]['duration'] = int(info.get('duration', 0)) + login_info_dict[userid][
                    'duration']
                if login_info_dict[userid].get('start_time') > info.get('entertime'):
                    login_info_dict[userid]['start_time'] = info.get('entertime')
                if login_info_dict[userid]['end_time'] < info.get('outtime'):
                    login_info_dict[userid]['end_time'] = info.get('outtime')
            else:
                login_info_dict[userid] = {}
                login_info_dict[userid] = {
                    'start_time': info.get('entertime'),
                    'end_time': info.get('outtime'),
                    'duration': int(info.get('duration', 0)),
                    'username': info.get('username'),
                    'userid': userid
                }
    for key, value in login_info_dict.items():
        start_time = login_info_dict[key]['start_time']
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').astimezone(tz=pytz.UTC)
        start_time = start_time - datetime.timedelta(hours=8)
        login_info_dict[key]['start_time'] = start_time
        end_time = login_info_dict[key]['end_time']
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').astimezone(tz=pytz.UTC)
        end_time = end_time - datetime.timedelta(hours=8)
        login_info_dict[key]['end_time'] = end_time
    return login_info_dict


def get_virtualclass_lesson(vc, user_student_infos):
    if vc.class_type_id == 1:  # 1对1
        vc.student_user_id = user_student_infos[0].id
        last_vc = VirtualclassInfo.objects.filter(student_user_id=vc.student_user_id, class_type_id=ClassType.ONE2ONE, status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL)).order_by('-start_time').first()
        if not last_vc:
            lesson = user_student_infos[0].lesson
            vc.first_course = 1
        else:
            lesson = get_next_lesson(last_vc.lesson)
            vc.first_course = 0
        if lesson:
            vc.lesson_id = lesson.id
            vc.lesson_no = lesson.lesson_no
        return vc
    else:  # 小班课
        student_user_ids = [user_student_info.id for user_student_info in user_student_infos]
        student_user_names = [user_student_info.real_name for user_student_info in user_student_infos]
        class_info = vc.class_field
        last_vc = VirtualclassInfo.objects.filter(class_field_id=class_info.id, class_type_id=ClassType.SMALLCLASS, status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL)).order_by('-start_time').first()
        if not last_vc:
            lesson = class_info.lesson
            vc.first_course = 1
        else:
            lesson = get_next_lesson(last_vc.lesson)
            vc.first_course = 0
        vc.lesson_id = lesson.id
        vc.lesson_no = lesson.lesson_no
        return vc

def create_tutor_timetable(vc):
    tutor_timetable = TutorTimetable()
    tutor_timetable.id = create_id()
    tutor_timetable.tutor_user_id = vc.tutor_user_id
    tutor_timetable.virtual_class_id = vc.id
    tutor_timetable.start_time = vc.start_time
    tutor_timetable.status = TutorTimetable.SUCCESS_APPOINTMENT
    tutor_timetable.end_time = vc.end_time
    tutor_timetable.class_field_id = vc.class_field_id
    tutor_timetable.class_type_id = vc.class_type_id
    tutor_timetable.student_user_id = vc.student_user_id
    tutor_timetable.save()
    return tutor_timetable

def tutor_timetable_data(vc):
    tutor_timetable = TutorTimetable.objects.filter(tutor_user_id=vc.tutor_user_id, start_time=vc.start_time).filter(
        ~Q(status=TutorTimetable.CANCELED_PUBLISH)).first()
    if tutor_timetable:
        if tutor_timetable.status == TutorTimetable.SUCCESS_APPOINTMENT:
            print('tutor_timetable error, old_virtual_class_id: {}, new_virtual_class_id: {}'.format(
                tutor_timetable.virtual_class_id, vc.id))
            tutor_timetable = create_tutor_timetable()
        else:
            tutor_timetable.status = TutorTimetable.SUCCESS_APPOINTMENT
            tutor_timetable.virtual_class_id = vc.id
            tutor_timetable.save()
    else:
        tutor_timetable = create_tutor_timetable(vc)
    return tutor_timetable

def create_student_timetable(vc, user_student_ids):
    student_timetables = StudentTimetable.objects.filter(student_user_id__in=user_student_ids, start_time=vc.start_time,
                                                         status__in=[StudentTimetable.SUCCESS_APPOINTMENT,
                                                                     StudentTimetable.OCCUPATION]).all()
    for student_timetable in student_timetables:
        if student_timetable.status == StudentTimetable.SUCCESS_APPOINTMENT:  # 学生课表已经有预约成功的数据，是错误数据
            print('student_timetable appointment data error, vc id is {}, student_timetable id is {}, student_timetable virtual_class_id is {}'.format(vc.id, student_timetable.id, student_timetable.virtual_class_id))
        elif student_timetable.status == StudentTimetable.OCCUPATION:
            if student_timetable.tutor_user_id == vc.tutor_user_id:
                student_timetable.status = StudentTimetable.SUCCESS_APPOINTMENT
                student_timetable.virtual_class_id = vc.id
                student_timetable.class_field_id = vc.class_field_id
                student_timetable.class_type_id = vc.class_type_id
                student_timetable.save()
                user_student_ids.remove(student_timetable.student_user_id)
                create_virtualclass_member(vc, student_timetable)
                continue
            else:
                print(
                    'student_timetable oppucation data error, vc id is {}, student_timetable id is {}, student_timetable virtual_class_id is {}'.format(
                        vc.id, student_timetable.id, student_timetable.virtual_class_id))
    for user_student_id in user_student_ids:
        student_timetable = StudentTimetable()
        student_timetable.id = create_id()
        student_timetable.tutor_user_id = vc.tutor_user_id
        student_timetable.student_user_id = user_student_id
        student_timetable.virtual_class_id = vc.id
        student_timetable.start_time = vc.start_time
        student_timetable.status = StudentTimetable.SUCCESS_APPOINTMENT
        student_timetable.class_type_id = vc.class_type_id
        student_timetable.class_field_id = vc.class_field_id
        student_timetable.end_time = vc.end_time
        student_timetable.save()
        create_virtualclass_member(vc, student_timetable)

def create_virtualclass_member(vc, student_timetable):
    virtualclass_member = ScheduleVirtualclassMember()
    virtualclass_member.student_timetable_id = student_timetable.id
    virtualclass_member.virtual_class_id = vc.id
    virtualclass_member.class_type_id = vc.class_type_id
    virtualclass_member.class_field_id = vc.class_field_id
    virtualclass_member.student_user_id = student_timetable.student_user_id
    history_vc = VirtualclassInfo.objects.filter(virtual_class_member__student_user_id=student_timetable.student_user_id, class_type_id=vc.class_type_id, status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL), start_time__lt=vc.start_time).first()
    if history_vc:
        virtualclass_member.first_course = 0
    else:
        virtualclass_member.first_course = 1
    both_history_vc = VirtualclassInfo.objects.filter(virtual_class_member__student_user_id=student_timetable.student_user_id, status__in=(VirtualclassInfo.FINISH_NOMAL, VirtualclassInfo.FINISH_ABNOMAL), tutor_user_id=vc.tutor_user_id, start_time__lt=vc.start_time).first()
    if both_history_vc:
        virtualclass_member.both_first_course = 0
    else:
        virtualclass_member.both_first_course = 1
    virtualclass_member.start_time = vc.start_time
    virtualclass_member.end_time = vc.end_time
    virtualclass_member.save()

def get_serial_path_list(authkey, startdate, enddate, page=1):
    '''获得20，21号所有在拓课上课的数据'''
    url = f'''https://global.talk-cloud.net/WebAPI/getSerialPathList/key/{authkey}/startdate/{startdate}/enddate/{enddate}/page/{page}/'''
    response = requests.get(url)
    result = response.json()
    room_list = result.get('roomlist')
    for room in room_list:
        # try:
            start_time = room.get('starttime')
            tk_class_id = room.get('serial')
            if tk_class_id == '109308101':
                print('error')
                continue
            bj_start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').astimezone(tz=pytz.UTC)
            utc_start_time = bj_start_time - datetime.timedelta(hours=8)
            vc = get_virtualclass_info(tk_class_id, start_time)
            if vc:
                continue
            logininfo_result = getlogininfo(tk_class_id)
            if not logininfo_result:
                print('not get logininfo, tk class id={}'.format(tk_class_id))
                continue
            user_tutor_info = get_user_tutor_info(logininfo_result)
            if not user_tutor_info:
                print('not found tutor, tk_class_id={}, room_info={}'.format(tk_class_id, json.dumps(room)))
                continue
            user_student_infos = get_user_student_infos(logininfo_result)
            vc = VirtualclassInfo.objects.filter(tutor_user_id=user_tutor_info.id,
                                                 start_time=utc_start_time,
                                                 class_type_id__in=(ClassType.ONE2ONE, ClassType.SMALLCLASS)
                                                 ).filter(~Q(status=VirtualclassInfo.CANCELED)).order_by('status').first()
            if vc:
                vc.tk_class_id = tk_class_id
                vc.save(update_fields=['tk_class_id', 'update_time'])
                continue
            if len(user_student_infos) == 0:
                print('not found student, tk_class_id={}, room_info={}'.format(tk_class_id, json.dumps(room)))
                continue
            serial_type = get_tk_room_type(tk_class_id)
            vc = VirtualclassInfo()
            vc.id = create_id()
            if serial_type == '3':
                vc.class_type_id = 2
                student_user_ids = [user_student_info.id for user_student_info in user_student_infos]
                class_info = get_class_info(student_user_ids)
                if not class_info:
                    print('not found class info, tk_class_id={}, room_info={}'.format(tk_class_id, json.dumps(room)))
                    continue
                vc.class_field = class_info
            vc.student_user_id = user_student_infos[0].id
            vc.class_type_id = 2 if serial_type == '3' else 1
            vc.tutor_user_id = user_tutor_info.id
            vc.tk_class_id = tk_class_id
            vc.start_time = utc_start_time
            vc.end_time = utc_start_time + datetime.timedelta(minutes=55)
            vc.status = VirtualclassInfo.FINISH_ABNOMAL
            vc.reason = 0
            vc.virtualclass_type_id = 1
            vc = get_virtualclass_lesson(vc, user_student_infos)
            tutor_enter_time, tutor_leave_time = get_tutor_enter_leave_time(logininfo_result)
            vc.actual_start_time = tutor_enter_time
            vc.actual_end_time = tutor_leave_time
            vc.save()
            tutor_timetable = tutor_timetable_data(vc)
            user_student_ids = [user_student_info.id for user_student_info in user_student_infos]
            create_student_timetable(vc, user_student_ids)
        # except Exception as e:
        #     print('error: {}'.format(e))
        #     print(json.dumps(room))

def getlogininfo(serial=''):

    '''获取房间用户登入登出情况'''

    if not serial:
        return {}
    params = {
        "key": authkey,
        "serial": serial
    }

    url = "http://global.talk-cloud.net/WebAPI/getlogininfo"
    try:
        result = requests.post(url, data=params)
        result = result.json()   # 0 是老师， 2是学员
        logininfo = result.get('logininfo', [])
        return logininfo
    except Exception as e:
        print('获取房间用户登录登出信息失败, err={}'.format(e))
    return {}


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--page',
                            dest='page',
                            default=1)

        parser.add_argument('--merged_parent_name',
                            dest='merged_parent_name',
                            default='')

    def handle(self, *args, **kwargs):
        # page = kwargs.get('page')
        for i in range(3, 12):
            time.sleep(1)
            print('start page {}'.format(i))
            get_serial_path_list('ex5lZksGvEmoeC1m', 1597852800, 1598025600, i)