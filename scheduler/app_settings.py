from django.conf import settings

EVENT_DURATION = getattr(settings, 'EVENT_DURATION', 55)

LOOK_BACK_BY_WEEK = getattr(settings, 'LOOK_BACK_BY_WEEK', 9)

LOOK_FORWARD_BY_WEEK = getattr(settings, 'LOOK_FORWARD_BY_WEEK', 7)

BAN_CANCLE_TIME = getattr(settings, 'BAN_CANCLE_TIME', 2)
