from course.models import Courseware
from urllib import parse, request
from Crypto.Cipher import AES
import requests
import json
import time
import hashlib
import logging
from django.conf import settings
logger = logging.getLogger(__name__)

'''
session
tk_cw_id
根据session获取到关联的courseware
将courseware 取出来上传到 拓课云 返回 拓课云课件ID
将ID 保存到 Courseware
'''

url_root = "http://global.talk-cloud.net/WebAPI/"
# dev : ScszQv2yD0yEPrkl
# stage : 30rHVsyEvTLKVwTY
domain = 'oks'
authkey = 'ex5lZksGvEmoeC1m'
if settings.SETTINGS_MODULE == 'ng_webapp.settings.dev' or settings.SETTINGS_MODULE == 'ng_webapp.settings.test':
    authkey = 'ScszQv2yD0yEPrkl'
    domain = 'dev'
elif settings.SETTINGS_MODULE == 'ng_webapp.settings.stage':
    authkey = '30rHVsyEvTLKVwTY'
    domain = 'stage'



def request_post(server_url, post_data):
    post_data = parse.urlencode(post_data).encode(encoding='utf-8')
    # print(post_data)
    req = request.Request(url=server_url, data=post_data)
    res = request.urlopen(req)
    res = res.read()
    res = res.decode(encoding="utf-8")
    # print(res)
    res = json.loads(res)

    return res


def create_tk_room(chairmanpwd, roomname, starttime,
                   endtime, assistantpwd, patrolpwd,
                   confuserpwd, autoopenav=1, roomtype=0):
    '''
    创建拓课房间
    :param chairmanpwd:
    :param roomname:
    :param starttime:
    :param endtime:
    :param assistantpwd: 助教密码
    :param patrolpwd: 巡课密码
    :param confuserpwd: 学生密码
    :return:
    '''

    url = url_root + "roomcreate/"
    post_data = {
        "key": authkey,
        "roomname": roomname,
        "starttime": starttime,
        "endtime": endtime,
        "chairmanpwd": chairmanpwd,
        "assistantpwd": assistantpwd,
        "patrolpwd": patrolpwd,
        "roomtype": roomtype,
        "videotype": 1,
        "passwordrequired": 0,
        "confuserpwd": confuserpwd,
        "autoopenav": 1,
        "roomlayout": 4
    }

    logger.debug('authkey is: {} setting {} '.format(authkey, settings.SETTINGS_MODULE))

    classid = request_post(url, post_data)['serial']
    return classid


def upload_cw_tk(filepath='', filename=''):
    # 在上传课件的时候,直接更新到到virtualclass
    # 通过sessionID 上传获取到相应的课件
    # 上传课件之后获取tk_cw_id
    # 在课件上传的时候更新tk中的课件
    if not filepath:
        return 0
    payload = {
        "key": authkey,
        "conversion": 1,
        'dynamicppt': 1,
        'isopen': 1,
    }
    file_read = open(filepath, 'rb')
    if filename:
        # file_read.name = filename
        file_read.raw.name = filename
    files = {
        "filedata": file_read
    }


    url = "http://global.talk-cloud.net/WebAPI/uploadfile"
    try:
        result = requests.post(url, data=payload, files=files)
        logger.debug(result.json())

        fileid = result.json()['fileid']
    except Exception as e:
        logger.error(e)
        fileid = 0

    return fileid


#获取房间用户登入登出情况
def getlogininfo(serial=''):

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
        logger.error('获取房间用户登录登出信息失败, err={}'.format(e))
    return {}


def deleteFile(fileId):
    payload = {
        "key": authkey,
        "fileidarr[]": str(fileId),
    }

    url = "http://global.talk-cloud.net/WebAPI/deletefile"
    result = request_post(url, payload)


def entry_class_path(serial, username, usertype, vc_id=0, course_session_id=0, student_id=0, tutor_id=0):
    """
    http://global.talk-cloud.net/WebAPI/entry?serial=1913645175&username=simon&usertype=2&ts=1550310506&auth=aa40c58cc19ce6081c0597015714cdf0&domain=oks
    domain 必填
    serial 必填 非0开始数字串
    username 必填 用户在房间中显示的名称, 使用utf-8编码, 特殊字符使用urlencode转义
    usertype 必填 0 讲师, 1 助教, 2 学员, 3 用户直播 4 巡检员
    ts  必填 时间戳 精确到秒
    auth 必填 MD5(key + ts + serial + usertype)
    jumpurl 选填 课程结束后, 自动跳转到指定的URL, 在参数的最后面传递这个参数.
    :param serial:
    :param roomname:
    :param username:
    :param usertype:
    :return:
    """

    timestamp = str(int(time.time()))

    authstr = authkey + timestamp + serial + str(usertype)
    authmd5 = hashlib.md5()
    authmd5.update(authstr.encode('utf-8'))
    authmd5 = authmd5.hexdigest()
    # jumpurl = 'http://192.168.200.200:8888/virtualclass/'
    jumpurl = 'https://{}/virtualclass/'.format(settings.HOST_NAME)
    if usertype == 0:
        jumpurl = jumpurl + 'tk_teacher_finish?vc_id={vc_id}&course_session_id={course_session_id}&student_id={student_id}'.format(vc_id=vc_id, course_session_id=course_session_id, student_id=student_id)
        userpassword = en_aes('lingoace')
        entrypath = 'http://global.talk-cloud.net/WebAPI/entry?serial={serial}&username={username}' \
                    '&userpassword={userpassword}&usertype=0&ts={ts}&auth={auth}&domain={domain}&jumpurl={jumpurl}'\
            .format(serial=serial, username=username, userpassword=userpassword,
                    ts=timestamp, auth=authmd5, domain=domain, jumpurl=jumpurl)
    elif usertype == 1:
        userpassword = en_aes('assistant')
        entrypath = 'http://global.talk-cloud.net/WebAPI/entry?serial={serial}&username={username}' \
                    '&userpassword={userpassword}&usertype=1&ts={ts}&auth={auth}&domain={domain}&jumpurl={jumpurl}'\
            .format(serial=serial, username=username, userpassword=userpassword,
                    ts=timestamp, auth=authmd5, domain=domain, jumpurl=jumpurl)
    elif usertype == 2:
        jumpurl = jumpurl + 'tk_student_finish?vc_id={vc_id}&course_session_id={course_session_id}&tutor_id={tutor_id}&pid={pid}'.format(vc_id=vc_id, course_session_id=course_session_id, tutor_id=tutor_id, pid=student_id)
        entrypath = 'http://global.talk-cloud.net/WebAPI/entry?serial={serial}&username={username}' \
                    '&usertype=2&ts={ts}&auth={auth}&domain={domain}&jumpurl={jumpurl}'\
            .format(serial=serial, username=username,
                    ts=timestamp, auth=authmd5, domain=domain, jumpurl=jumpurl)
    else:
        userpassword = en_aes('patrol')
        entrypath = 'http://global.talk-cloud.net/WebAPI/entry?serial={serial}&username={username}' \
                    '&userpassword={userpassword}&usertype=4&ts={ts}&auth={auth}&domain={domain}&jumpurl={jumpurl}'\
            .format(serial=serial, username=username, userpassword=userpassword,
                    ts=timestamp, auth=authmd5, domain=domain, jumpurl=jumpurl)

    return entrypath


def bind_courseware_tk(roomid, tk_file_id, defaultId=0):
    url = url_root + 'roombindfile/'
    post_data ={
        'key': authkey,
        'serial': roomid,
        'fileid': defaultId,
        'fileidarr[]': str(tk_file_id),
    }
    return request_post(url, post_data)


def en_aes(data):
    import binascii
    aes = AES.new(add_to_16(authkey), AES.MODE_ECB)
    encrypted_text = binascii.b2a_hex(aes.encrypt(add_to_16(data))).decode('ascii')  # 正确结果应该是e55a0e256f9c805abdca8ee013844532
    return encrypted_text


def add_to_16(text):
    while len(text) % 16 != 0:
        text += '\0'
    return str.encode(text)


def seeze_tk_record(serial):
    """
    get tk mp4 record url
    :param serial:
    :return:
    """
    payload = {
        "key": authkey,
        "serial": serial,
        "recordtype": "1",
    }

    url = "http://global.talk-cloud.net/WebAPI/getrecordlist"
    result = request_post(url, payload)
    if result['result'] != 0:
        logger.error("获得课堂视频出错, result={}, args={}".format(result, payload))
        return "null"
    mp4_url = result['recordlist'][0]['https_playpath_mp4']
    return mp4_url


def get_tk_room_file(serial):
    '''
    获取房间的文档列表
    serial: 拓课房间号
    '''
    tk_file_list = []
    url = 'http://global.talk-cloud.net/WebAPI/getroomfile'
    params = {
        'key': authkey,
        'serial': serial
    }
    response = requests.get(url, params)
    result = response.json()
    if result.get('result'):
        logger.debug(result)
        return tk_file_list
    for file in result.get('roomfile', []):
        if file.get('active') == '1':
            tk_file_list.append(file.get('fileid'))
    return tk_file_list


def tk_room_delete_file(serial, file_list):
    '''
    某个房间删除关联的相应文档
    :param serial:  房间号
    :param file_list:  文件id数组
    :return:
    '''
    if serial:
        serial = int(serial)

    data = {
        'key': authkey,
        'serial': serial,
        'fileidarr': file_list  # 数组
    }

    url = 'http://global.talk-cloud.net/WebAPI/roomdeletefile'

    result = requests.post(url, data=data)
    result = result.json()
    return result
