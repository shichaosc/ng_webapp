from webapp.models import *
from django.core.management.base import BaseCommand
from webapp.utils import print_insert_table_times
from webapp.new_model_add import CreateTutor


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--max_id',
                            dest='max_id',
                            default='')

    @print_insert_table_times
    def add_tutor(self, tutor_max_id):
        '''
        添加老师
        :return:
        '''
        tutors = Tutor.objects.filter(user_id__gt=tutor_max_id).all()
        for tutor in tutors:

            create_tutor = CreateTutor(tutor)
            create_tutor.add_tutor()

    def handle(self, *args, **options):

        # TutorInfo.objects.all().delete()
        # BalanceChange.objects.filter(role=BalanceChange.TEACHER).all().delete()

        tutor_max_id = int(options.get('max_id', 0))

        # 老师
        self.add_tutor(tutor_max_id)










