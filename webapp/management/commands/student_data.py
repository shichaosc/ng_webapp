from webapp.models import *
from django.core.management.base import BaseCommand
from webapp.utils import print_insert_table_times
from webapp.new_model_add import CreateStudent


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--max_id',
                            dest='max_id',
                            default='')

    @print_insert_table_times
    def add_student(self, student_max_id):

        tutor_ids = Tutor.objects.all().values_list('user_id')
        ambassador_ids = Ambassador.objects.all().values_list('user_id')
        students = User.objects.filter(id__gt=student_max_id).exclude(id__in=tutor_ids).exclude(id__in=ambassador_ids)

        for student in students:

            create_student = CreateStudent(student)
            create_student.add_student()

    def handle(self, *args, **options):

        student_max_id = int(options.get('max_id', 0))
        # 学生和家长
        self.add_student(student_max_id)
