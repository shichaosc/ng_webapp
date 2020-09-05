from django.db import models
from tutor import utils
from scheduler.models import TutorTimetable
from django.utils import timezone


class TutorManager(models.Manager):

    @classmethod
    def filter_by_weekdays(cls, weekdays=[], timedif=[]):
        now_time = timezone.now()
        tutor_time_table = TutorTimetable.objects.filter(start_time__gt=now_time, status=TutorTimetable.PUBLISHED).all()
        query_list = []
        if weekdays:
            weekdays = ','.join(weekdays)
            query_list.append("WEEKDAY(CONVERT_TZ(start_time, '+00:00', '+08:00')) in ({})".format(weekdays))
        if timedif:
            time_query_list = []
            for time_str in timedif:
                time_str_list = time_str.split('-')
                start_time, end_time = time_str_list[0], time_str_list[1]
                time_query_list.append("(TIME(CONVERT_TZ(start_time, '+00:00', '+08:00'))>='{}' and TIME(CONVERT_TZ(start_time, '+00:00', '+08:00'))<='{}')".format(start_time, end_time))
            time_query_str = ' or '.join(time_query_list)
            query_list.append(time_query_str)
        tutor_time_table = tutor_time_table.extra(
            where=query_list
        )
        users = [tutor_publish.tutor_user for tutor_publish in tutor_time_table]
        return users




