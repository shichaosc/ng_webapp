from webapp.models import *
from django.core.management.base import BaseCommand
from scheduler.models import TutorTimetable
from django.db.models import F, Q
from classroom.models import VirtualclassInfo
from tutor.models import TutorInfo
import random
from webapp.utils import print_insert_table_times
from classroom.models import ClassInfo, VirtualclassType
from student.models import UserStudentInfo
from classroom import classroom_controller
from scheduler.models import ScheduleVirtualclassMember, StudentTimetable

start_id = 1000000000000000
end_id = 10000000000000000


class Command(BaseCommand):

    def add_tutor_event(self, user: User, tutor_info: TutorInfo):

        now_time = timezone.now()
        events = Event.objects.filter(start__lt=F('end_recurring_period'), user=user, end_recurring_period__gt=now_time).all()

        occurrences = []
        for event in events:
            logger.debug('event item: {0}'.format(event))
            occurrences_of_e = event.get_occurrence_list(now_time, event.end_recurring_period)
            occurrences.extend(occurrences_of_e)

        all_subscriptions = EventSubscription.objects.filter(end_time__gt=now_time, event__user__id=user.id)

        subscription_occurrence_list = []

        for subscription in all_subscriptions:
            subscription_occurrences = subscription.get_occurrence_list_v2(subscription.start_time, subscription.end_time)
            subscription_occurrence_list.extend(subscription_occurrences)

        subscription_dict = {}
        for sub_occurrence in subscription_occurrence_list:
            subscription_dict[sub_occurrence.start] = sub_occurrence

        for occurrence in occurrences[::-1]:
            event_start = occurrence.start
            if event_start in subscription_dict.keys():
                occurrences.remove(occurrence)
        subscription_occurrence_list.extend(occurrences)

        for occurrence in subscription_occurrence_list:

            if occurrence.start < now_time:
                continue

            if occurrence.is_occupied == 0:  # 老师发布
                tutor_time_table = TutorTimetable()
                tutor_time_table.id = random.randint(start_id, end_id)
                tutor_time_table.tutor_user = tutor_info
                tutor_time_table.start_time = occurrence.start
                tutor_time_table.end_time = occurrence.end
                tutor_time_table.status = TutorTimetable.PUBLISHED
                tutor_time_table.save()
            elif occurrence.is_occupied == 2:  # 预约
                if occurrence.has_virtualclass:  # 有virtualclass 跳过
                    continue
                vc_info = self.create_virtualclass(occurrence, tutor_info)

                tutor_time_table = TutorTimetable()
                tutor_time_table.id = random.randint(start_id, end_id)
                tutor_time_table.tutor_user = tutor_info
                tutor_time_table.class_type_id = vc_info.class_type_id
                tutor_time_table.start_time = occurrence.start
                tutor_time_table.end_time = occurrence.end
                tutor_time_table.student_user = vc_info.student_user
                tutor_time_table.status = TutorTimetable.SUCCESS_APPOINTMENT
                tutor_time_table.virtual_class = vc_info
                tutor_time_table.class_field = vc_info.class_field
                tutor_time_table.save()
            elif occurrence.is_occupied == 1:  # 预占
                student_info = UserStudentInfo.objects.filter(real_name=occurrence.subscription_stu_name).first()
                tutor_time_table = TutorTimetable()
                tutor_time_table.id = random.randint(start_id, end_id)
                tutor_time_table.tutor_user = tutor_info
                tutor_time_table.class_type_id = occurrence.class_type_id
                tutor_time_table.start_time = occurrence.start
                tutor_time_table.end_time = occurrence.end
                tutor_time_table.student_user = student_info
                tutor_time_table.status = TutorTimetable.OCCUPATION
                tutor_time_table.class_field = self.get_vc_classInfo(occurrence)
                tutor_time_table.save()

                student_names = occurrence.student_names
                for name in student_names:
                    student_info = UserStudentInfo.objects.filter(parent_user__username=name).first()
                    # student_info.id = random.randint(start_id, end_id)
                    student_time_table = StudentTimetable()
                    student_time_table.id = random.randint(start_id, end_id)
                    student_time_table.tutor_user = tutor_info
                    student_time_table.class_type_id = occurrence.class_type_id
                    student_time_table.student_user = student_info
                    student_time_table.class_field = self.get_vc_classInfo(occurrence)
                    student_time_table.start_time = occurrence.start
                    student_time_table.end_time = occurrence.end
                    student_time_table.status = StudentTimetable.OCCUPATION
                    student_time_table.save()

    def create_virtualclass(self, occurrence, tutor_user):

        vc_info = VirtualclassInfo()
        vc_info.id = random.randint(start_id, end_id)
        vc_info.class_field = self.get_vc_classInfo(occurrence)
        vc_info.class_type_id = occurrence.class_type_id
        student_user = UserStudentInfo.objects.filter(parent_user__username=occurrence.subscription_invitee).first()
        vc_info.tutor_user = tutor_user
        vc_info.virtualclass_type_id = VirtualclassType.TK
        vc_info.student_user = student_user
        vc_info.start_time = occurrence.start
        vc_info.end_time = occurrence.end
        vc_info.first_course = VirtualclassInfo.NOT_FIRST_COURSE
        vc_info.status = VirtualclassInfo.NOT_START
        # vc_info.tk_class_id = self.create_tk_room(occurrence)
        vc_info.save()
        self.add_student_time_table(vc_info, occurrence)
        return vc_info

    def add_student_time_table(self, vc_info, occurrence):
        student_names = occurrence.student_names
        for name in student_names:
            student_info = UserStudentInfo.objects.filter(parent_user__username=name).first()
            student_time_table = StudentTimetable()
            student_time_table.id = random.randint(start_id, end_id)
            student_time_table.tutor_user = vc_info.tutor_user
            student_time_table.class_type_id = vc_info.class_type_id
            student_time_table.student_user = student_info
            student_time_table.class_field = vc_info.class_field
            student_time_table.start_time = vc_info.start_time
            student_time_table.end_time = vc_info.end_time
            student_time_table.virtual_class = vc_info
            student_time_table.status = StudentTimetable.SUCCESS_APPOINTMENT
            student_time_table.save()
            self.add_virtualclass_member(vc_info, student_info, student_time_table)

    def add_virtualclass_member(self, vc_info, student_info, student_time_table):
        member = ScheduleVirtualclassMember()
        member.virtual_class = vc_info
        member.student_user = student_info
        member.class_type_id = vc_info.class_type_id
        member.first_course = ScheduleVirtualclassMember.NO
        member.start_time = vc_info.start_time
        member.student_timetable = student_time_table
        member.save()

    def create_tk_room(self, occurrence):
        roomname = occurrence.subscription_invitee
        chairmanpwd = 'lingoace'
        # 设置虚拟课堂开始上课时间
        starttime = time.time()  # 生成appointment 的时候创建虚拟教室
        # 设置虚拟课堂结束时间
        end_time = time.mktime(occurrence.start.timetuple())

        endtime = end_time + 1 * 24 * 3600  # 教室保留1天自动消除.
        assistantpwd = 'assistant'
        patrolpwd = 'patrol'
        confuserpwd = 'student'
        autoopenav = 1
        roomtype = 1 if occurrence.class_type_id == 1 else 3
        classid = classroom_controller.create_tk_room(chairmanpwd, roomname, starttime,
                                                      endtime, assistantpwd, patrolpwd,
                                                      confuserpwd, roomtype)
        return classid

    def get_vc_classInfo(self, occurrence):
        class_info = None
        if occurrence.class_type_id == 2:
            class_info = ClassInfo.objects.filter(leader_user__parent_user__username=occurrence.subscription_invitee, user_num__gt=0).first()
        return class_info


    @print_insert_table_times
    def handle(self, *args, **options):

        tutors = Tutor.objects.all()

        for tutor in tutors:
            if tutor.user.username == '钱爽':
                pass
            tutor_info = TutorInfo.objects.filter(username=tutor.user.username).first()
            if not tutor_info:
                continue
            self.add_tutor_event(tutor.user, tutor_info)



