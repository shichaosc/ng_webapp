from django.core.management.base import BaseCommand
from classroom.classroom_controller import getlogininfo
from classroom.models import VirtualclassInfo
from scheduler.models import ScheduleVirtualclassMember
import requests
import datetime
from student.models import UserStudentInfo

domain = 'oks'
authkey = 'ex5lZksGvEmoeC1m'

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
        result = result.json()
        logininfo = result.get('logininfo', [])
        return logininfo
    except Exception as e:
        print('获取房间用户登录登出信息失败, err={}'.format(e))
    return {}


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--virtual_class_id',
                            dest='virtual_class_id',
                            default='')


    def get_student_logininfo(self, vc):

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
        return login_info_dict

    def update_virtualclass_member(self, vc):

        virtualclass_members = ScheduleVirtualclassMember.objects.filter(virtual_class_id=vc.id).all()
        login_info_dict = self.get_student_logininfo(vc)

        for virtualclass_member in virtualclass_members:
            student_user_id = virtualclass_member.student_user_id
            student_login_info = login_info_dict.get(student_user_id, None)
            if student_login_info:
                enter_time = datetime.datetime.strptime(student_login_info.get('start_time'), '%Y-%m-%d %H:%M:%S')
                enter_time = enter_time - datetime.timedelta(hours=8)
                leave_time = datetime.datetime.strptime(student_login_info.get('end_time'), '%Y-%m-%d %H:%M:%S')
                leave_time = leave_time - datetime.timedelta(hours=8)
                virtualclass_member.enter_time = enter_time
                virtualclass_member.leave_time = leave_time
                virtualclass_member.save(update_fields=['enter_time', 'leave_time', 'update_time'])
                print(student_login_info)

    def handle(self, *args, **kwargs):

        virtual_class_id = kwargs.get('virtual_class_id')

        if virtual_class_id:

            virtual_class = VirtualclassInfo.objects.filter(id=virtual_class_id).first()

            if virtual_class:
                self.update_virtualclass_member(virtual_class)
        else:
            virtual_classes = VirtualclassInfo.objects.filter(status=3, class_type_id=3).all()

            for virtual_class in virtual_classes:
                self.update_virtualclass_member(virtual_class)

