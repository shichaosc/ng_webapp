from classroom.models import ClassType


def get_tk_roomtype(vc_type):
    """
    返回TK教室类型
    :param vc_type: 班级类型 smallcass oneonone
    :return: 0 是一对一教室 3是一对多教室
    """
    if not vc_type:
        return 0
    if vc_type == ClassType.objects.get_smallclass_type():
        return 3
    else:
        return 0