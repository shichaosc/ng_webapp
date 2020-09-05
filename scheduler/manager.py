from scheduler.models import TutorTimetable
from scheduler.abstract_model import Occurrence
from datetime import timedelta

class TutorSchedulerManager(object):

    @classmethod
    def get_occurrence_list(cls, tutor, start, end):

        if isinstance(tutor, int) or isinstance(tutor, str):
            tutor_id = tutor
        else:
            tutor_id = tutor.id
        occurrences = []
        events = TutorTimetable.objects.filter(tutor_user_id=tutor_id, start_time__lt=end, start_time__gte=start).exclude(status=TutorTimetable.CANCELED_PUBLISH)
        for event in events:
            if event.student_user:
                occurrence = Occurrence(str(event.id), event.start_time, event.end_time, event.student_user.real_name, event.status, event.class_type_id)
            else:
                occurrence = Occurrence(str(event.id), event.start_time, event.end_time, '', event.status, event.class_type_id)
            occurrences.append(occurrence)

        subscription_dict = {}
        for sub_occurrence in occurrences:
            if sub_occurrence.status in (TutorTimetable.OCCUPATION, TutorTimetable.SUCCESS_APPOINTMENT):
                subscription_dict[sub_occurrence.start] = sub_occurrence

        for occurrence in occurrences[::-1]:
            event_start = occurrence.start
            before_event_start = event_start + timedelta(minutes=-30)
            next_event_start = event_start + timedelta(minutes=30)
            if (before_event_start in subscription_dict.keys()) or (next_event_start in subscription_dict.keys()):
                occurrence.status = 4
        return occurrences
