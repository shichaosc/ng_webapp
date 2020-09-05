from django.core.management.base import BaseCommand
from classroom.models import VirtualclassInfo

start_id = 1000000000000000
end_id = 10000000000000000


class Command(BaseCommand):

    def handle(self, *args, **options):

        vc_list = VirtualclassInfo.objects.filter(lesson_id__isnull=False, lesson_no__isnull=True).all()

        for vc in vc_list:
            lesson = vc.lesson
            vc.lesson_no = lesson.lesson_no
            vc.save()
