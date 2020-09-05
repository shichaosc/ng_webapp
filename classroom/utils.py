from classroom.models import ClassType


CLASS_TYPE_NAME_SMALL_CLASS = 2   # 小班课
CLASS_TYPE_NAME_ONE_ON_ONE = 1   # 一对一

TK_CLASS_ROOM = 1   # 拓客
BAIJIAYUN_ROOM = 2   # 百家云

AGORA_CLASS_ROOM_NAME = 'Agaro'
TK_CLASS_ROOM_NAME = 'Tk'


def is_small_class(vc_type):
    if not vc_type:
        return False
    if int(vc_type) == 2:
        return True
    else:
        return False


def get_tk_roomtype(vc_type):
    """
    返回TK教室类型
    :param vc_type: 班级类型 smallcass oneonone
    :return: 0 是一对一教室 3是一对多教室
    """
    if not vc_type:
        return 0
    if vc_type == CLASS_TYPE_NAME_SMALL_CLASS:
        return 3
    else:
        return 0


def cmp_tutor_match(tutor1, tutor2):
    '''

    :param tutor1: dict {'id': '', 'publish_count': '', 'no_publish_count': ''}
    :param tutor2:
    :return:
    '''

    if tutor1.get('publish_count', 0) > tutor2.get('publish_count', 0):
        return -1

    elif tutor1.get('publish_count', 0) == tutor2.get('publish_count', 0):
        if tutor1.get('no_publish_count', 0) > tutor2.get('no_publish_count', 0):
            return -1
        elif tutor1.get('no_publish_count', 0) == tutor2.get('no_publish_count', 0):
            return 0
        else:
            return 1
    else:
        return 1
