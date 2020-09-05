import datetime, logging
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from ng_webapp import utils
from tutor.models import TutorInfo
from django.core.serializers.json import DjangoJSONEncoder
import json
from scheduler.models import TutorTimetable
from scheduler.manager import TutorSchedulerManager

logger = logging.getLogger(__name__)

CLASS_TYPE_NAME_SMALL_CLASS = 'smallclass'
CLASS_TYPE_NAME_ONE_ON_ONE = 'oneonone'


@permission_required('virtualclass.can_monitor_virtualclass')
def man_event(request):

    user_id = request.GET.get('user')
    date = request.GET.get('date')
    action = request.GET.get('action')
    d, t_monday, t_next_monday = utils.get_one_week_range_v2(date, action)
    tutor = TutorInfo.objects.filter(id=user_id).first()
    occurrences = TutorSchedulerManager.get_occurrence_list(user_id, t_monday, t_next_monday)

    return render(request, 'scheduler/man_event.html',
                  {'occurrences': json.dumps([o.__dict__ for o in occurrences], cls=DjangoJSONEncoder),
                   'date': d,
                   'event_duration': TutorTimetable.default_event_duration,
                   'tutor': tutor,
                   'user': user_id
                   })


