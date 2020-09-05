from django.core.management.base import BaseCommand
from scheduler.models import TutorTimetable, StudentTimetable, ScheduleVirtualclassMember
from django.db import connections
from classroom.models import VirtualclassInfo
from django.forms.models import model_to_dict
import logging

logger = logging.getLogger('pplingo.ng_webapp.scripts')

'''
删除学生重复约课数据(未上), 
student_timetable,
tutor_timetable, 
virtualclass_info, 
virtualclass_member
'''


class Command(BaseCommand):

    def query_repeat_data(self):

        sql = '''select sst.student_user_id, sst.start_time, count(*), GROUP_CONCAT(sst.virtual_class_id separator "-") from schedule_student_timetable sst 
left join classroom_virtualclass_info cvi on cvi.id=sst.virtual_class_id
left join schedule_tutor_timetable stt on stt.virtual_class_id=cvi.id
where sst.status<>0 and sst.start_time>'2020-08-01 00:00:00' and cvi.status=1 and stt.status<>0 and cvi.class_type_id in(1,2)
group by sst.student_user_id, sst.start_time having count(*)>1'''

        logger.debug(f'query repeate timetable sql: {sql}')

        with connections['lingoace'].cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                student_user_id = row[0]
                start_time = row[1]
                count = row[2]
                virtual_class_ids = row[3]
                self.judge_data(student_user_id, start_time, virtual_class_ids)

    def judge_data(self, student_user_id, start_time, virtual_class_ids):
        logger.debug(f'virtual_class_list: {student_user_id}')
        virtual_class_list = virtual_class_ids.split('-')
        virtual_class_list = list(set(virtual_class_list))
        if len(virtual_class_list) <= 1:
            '''删除student timetable, tutor_timetable, schedule_virtual_class_member'''
            student_timetables = StudentTimetable.objects.filter(virtual_class_id__in=virtual_class_list, status__in=(StudentTimetable.SUCCESS_APPOINTMENT, StudentTimetable.PUBLISHED, StudentTimetable.OCCUPATION)).all()
            if len(student_timetables) > 1:
                self.delete_repeat_student_timetable(student_timetables)

            tutor_timetables = TutorTimetable.objects.filter(virtual_class_id__in=virtual_class_list, status__in=(TutorTimetable.SUCCESS_APPOINTMENT, TutorTimetable.PUBLISHED)).all()
            if len(tutor_timetables) > 1:
                self.delete_repeat_tutor_timetable(tutor_timetables)
            return
        self.delete_repeat_virtualclass_info(virtual_class_list)

    def delete_repeat_student_timetable(self, student_timetables):
        normal_student_timetable_id = 0
        for student_timetable in student_timetables:
            virtual_class_members = ScheduleVirtualclassMember.objects.filter(student_timetable_id=student_timetable.id).all()
            if len(virtual_class_members) >= 1:
                if student_timetable.status == StudentTimetable.SUCCESS_APPOINTMENT:
                    normal_student_timetable_id = student_timetable.id

        for student_timetable in student_timetables:
            if student_timetable.id == normal_student_timetable_id:
                continue
            logger.debug('delete student timetable: {}'.format(model_to_dict(student_timetable)))
            student_timetable.delete()
        return

    def delete_repeat_tutor_timetable(self, tutor_timetables):
        normal_tutor_timetable_id = 0
        for tutor_timetable in tutor_timetables:
            if tutor_timetable.status == TutorTimetable.SUCCESS_APPOINTMENT:
                normal_tutor_timetable_id = tutor_timetable.id

        for tutor_timetable in tutor_timetables:
            if tutor_timetable.id == normal_tutor_timetable_id:
                continue
            print(model_to_dict(tutor_timetable))
            logger.debug('delete tutor timetable: {}'.format(model_to_dict(tutor_timetable)))
            tutor_timetable.delete()
        return

    def delete_repeat_virtualclass_info(self, virtual_class_list):
        not_delete_virtual_class = 0
        if len(virtual_class_list) <= 1:
            return
        for virtual_class_id in virtual_class_list:
            virtual_class = VirtualclassInfo.objects.filter(id=virtual_class_id).first()
            if not virtual_class:
                return
            tutor_timetable = TutorTimetable.objects.filter(virtual_class_id=virtual_class.id, status=TutorTimetable.SUCCESS_APPOINTMENT).first()
            if not tutor_timetable:
                continue
            virtual_class_members = ScheduleVirtualclassMember.objects.filter(virtual_class_id=virtual_class.id).all()
            if len(virtual_class_members) < 1:
                continue
            not_delete_virtual_class = virtual_class_id
        virtual_class_list.remove(not_delete_virtual_class)
        logger.debug('delete, virtualclass')
        logger.debug(virtual_class_list)
        VirtualclassInfo.objects.filter(id__in=virtual_class_list).delete()

    def handle(self, *args, **options):
        logger.debug('----------start--------')
        self.query_repeat_data()
        logger.debug('----------success--------')
