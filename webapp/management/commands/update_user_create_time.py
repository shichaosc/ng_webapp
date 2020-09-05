from django.core.management.base import BaseCommand
from webapp.models import User
from tutor.models import TutorInfo
from student.models import UserParentInfo
from datetime import datetime
import pytz


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_time = datetime.strptime('2020-01-15 00:00:00', '%Y-%m-%d %H:%M:%S').astimezone(pytz.UTC)
        parent_infos = UserParentInfo.objects.filter(create_time__lte=create_time).all()

        for parent_info in parent_infos:
            user = User.objects.filter(username=parent_info.username).first()
            if user:
                parent_info.create_time = user.date_joined
                parent_info.save()
