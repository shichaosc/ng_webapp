from django.core.management.base import BaseCommand
from scheduler.models import StudentTimetable, ScheduleVirtualclassMember
from classroom.models import VirtualclassInfo
import logging
from student.models import UserStudentInfo
logger = logging.getLogger('pplingo.ng_webapp.scripts')
import random
1000000000000000
8999999999999999
class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        virtual_class_ids = [1361839993794721,
                            1558329733224610,
                            1780310471977708,
                            2242180510286027,
                            2543202179358333,
                            2704852053797440,
                            2790090715212145,
                            3445010481893903,
                            4757064256304186,
                            5399199960532939,
                            5472604866131609,
                            5770356233007767,
                            6367762897113995,
                            6906108435388878,
                            7135043633689587,
                            7486393593608400,
                            7515976762446828,
                            8193853967641999,
                            8381122313818886,
                            8875869369613687]
        virtual_class_list = VirtualclassInfo.objects.filter(id__in=virtual_class_ids).all()
        for vc in virtual_class_list:
            student_time_table_id = random.randint(1000000000000000, 8999999999999999)
            student_time_table = StudentTimetable()
            student_time_table.id = student_time_table_id
            student_time_table.tutor_user_id = vc.tutor_user_id
            student_time_table.class_type_id = vc.class_type_id
            student_time_table.student_user_id = 8549171996842916
            student_time_table.class_field_id = vc.class_field_id
            student_time_table.start_time = vc.start_time
            student_time_table.end_time = vc.end_time
            student_time_table.virtual_class_id = vc.id
            student_time_table.status = StudentTimetable.SUCCESS_APPOINTMENT
            student_time_table.save()
            virtualclass_member = ScheduleVirtualclassMember()
            virtualclass_member.virtual_class_id = vc.id
            virtualclass_member.student_timetable_id = student_time_table.id
            virtualclass_member.class_field_id = vc.class_field_id
            virtualclass_member.student_user_id = 8549171996842916
            virtualclass_member.class_type_id = vc.class_type_id
            virtualclass_member.first_course = vc.first_course
            virtualclass_member.both_first_course = vc.first_course
            virtualclass_member.start_time = vc.start_time
            virtualclass_member.save()

