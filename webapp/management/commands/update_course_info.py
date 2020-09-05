from webapp.models import *
from django.core.management.base import BaseCommand
from webapp.utils import print_insert_table_times
from classroom.models import ClassInfo, VirtualclassInfo, ClassMember



class Command(BaseCommand):


    def add_arguments(self, parser):

        parser.add_argument('--static_url',
                            dest='static_url',
                            default='')


    @print_insert_table_times
    def handle(self, *args, **options):

        class_infos = ClassInfo.objects.filter(course_id__isnull=True).all()

        for class_info in class_infos:
            student_user = class_info.creator_user
            if not student_user:
                continue
            class_info.course_id = student_user.course_id
            class_info.course_edition_id = student_user.course_edition_id
            class_info.course_level = student_user.course_level
            class_info.lesson_id = student_user.lesson_id
            class_info.lesson_no = student_user.lesson_no
            class_info.first_course = student_user.first_course
            class_info.user_num = 1
            class_info.save()

            class_member = ClassMember()

            class_member.class_field = class_info
            class_member.student_user = student_user
            class_member.role = ClassMember.MONITOR
            class_member.save()

