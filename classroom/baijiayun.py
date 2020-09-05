from django.conf import settings
import hashlib
from urllib import parse
from classroom.models import ClassType
import time
from utils import utils


# md5 加密
def md5_str(sign_str):

    hmd5 = hashlib.md5()

    hmd5.update(sign_str.encode("utf8"))

    sign = hmd5.hexdigest()

    print('sign:', sign)

    return sign


# 旁听
def monitor_baijiayun(room_id, user_number, user_name, user_role=2, user_avatar=''):

    sign_str = '''room_id={}&user_avatar={}&user_name={}&user_number={}&user_role={}&partner_key={}'''.format(room_id, user_avatar, user_name, user_number, user_role, settings.PARTNER_KEY)

    sign = md5_str(sign_str)

    user_name = parse.quote(user_name)

    user_avatar = parse.quote(user_avatar)

    monitor_url = '''http://{baijiayun_domain}.at.baijiayun.com/web/room/enter?room_id={room_id}&user_number={user_number}&user_name={user_name}&user_role={user_role}&user_avatar={user_avatar}&sign={sign}'''.format(
        baijiayun_domain=settings.BAIJIAYUN_DOMAIN,
        room_id=room_id, user_number=user_number, user_name=user_name,
        user_role=user_role, user_avatar=user_avatar, sign=sign
    )

    # params = dict(
    #     room_id=room_id,
    #     user_number=user_number,
    #     user_name=user_name,
    #     user_role=user_role,
    #     user_avatar=user_avatar,
    #     sign=sign
    # )
    #
    # monitor_url = 'http://{baijiayun_domain}.at.baijiayun.com/web/room/enter?' + parse.urlencode(params)

    return monitor_url


# 视频回放
def playback(room_id):

    token = video_token(room_id)

    if not token:
        return None

    play_back_url = 'http://{private_domain}.at.baijiayun.com/web/playback/index?classid={class_id}&token={token}'.format(
        private_domain=settings.BAIJIAYUN_DOMAIN,
        class_id=room_id,
        token=token
    )
    return play_back_url


# 获取视频回放token
def video_token(room_id, expires_in=0):

    timestamp = time.time()

    sign_str = 'expires_in={expires_in}&partner_id={partner_id}&room_id={room_id}&timestamp={timestamp}&partner_key={partner_key}'.format(
        expires_in=expires_in,
        partner_id=settings.PARTNER_ID,
        room_id=room_id,
        timestamp=timestamp,
        partner_key=settings.PARTNER_KEY
    )

    sign = md5_str(sign_str)

    url = 'https://{}.at.baijiayun.com/openapi/playback/getPlayerToken'.format(settings.BAIJIAYUN_DOMAIN)

    params = {
        'partner_id': settings.PARTNER_ID,
        'room_id': room_id,
        'expires_in': expires_in,
        'timestamp': timestamp,
        'sign': sign
    }

    result = utils.fetch_post_api(url, params)

    if result:
        token = result.get('data', {}).get('token')
        return token
    return None
