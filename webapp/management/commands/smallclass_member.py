from webapp.models import *
from django.core.management.base import BaseCommand
from classroom.models import ClassInfo, ClassMember
import random
from student.models import UserStudentInfo
from webapp.utils import print_insert_table_times
from django.db import connections
from webapp.app_settings import START_ID, END_ID


class Command(BaseCommand):

    @print_insert_table_times
    def handle(self, *args, **options):
        # learning_group_list = []
        # with connections['pplingodb'].cursor() as cursor:
        #     sql = '''select learning_group_id from student_membership group by learning_group_id having count(learning_group_id)>1'''
        #     cursor.execute(sql)
        #     rows = cursor.fetchall()
        #     for row in rows:
        #         learning_group_list.append(row[0])

        learning_group_list = LearningGroup.objects.filter(virtual_class_type_id=ClassType.SMALLCLASS, status=LearningGroup.OPEN).all()

        for learning_group in learning_group_list:

            member_ships = Membership.objects.filter(learning_group_id=learning_group.id).all()
            monitor = member_ships.filter(role=Membership.Monitor).first()
            if not monitor:
                continue
            class_info = ClassInfo.objects.filter(creator_user__real_name=monitor.group_member.username).last()
            if not class_info:
                monitor_info = UserStudentInfo.objects.filter(real_name=monitor.group_member.username).first()

                class_info = ClassInfo()
                class_info.id = random.randint(START_ID, END_ID)
                class_info.creator_user = monitor_info
                class_info.leader_user = monitor_info
                class_info.class_type_id = ClassType.SMALLCLASS
                class_info.first_course = monitor_info.first_course
                class_info.user_num = 0
                class_info.class_name = monitor_info.real_name
                class_info.save()
            print(learning_group.id, '-----', class_info.id)
            for member_ship in member_ships:
                user = member_ship.group_member
                print(user.id, 'role', member_ship.get_role_display())
                student_info = UserStudentInfo.objects.filter(real_name=user.username).first()
                class_member = ClassMember.objects.filter(class_field=class_info, student_user=student_info).first()
                if class_member:
                    continue
                class_member = ClassMember()
                class_member.class_field = class_info
                class_member.student_user = student_info
                class_member.role = ClassMember.MEMBER
                if user.username == monitor.group_member.username:
                    class_member.role = ClassMember.MONITOR
                    class_info.course_id = student_info.course_id
                    class_info.course_edition_id = student_info.course_edition_id
                    class_info.course_level = student_info.course_level
                    class_info.lesson_id = student_info.lesson_id
                    class_info.lesson_no = student_info.lesson_no
                class_member.save()
                class_info.user_num = class_info.user_num + 1
                class_info.first_course = ClassInfo.NOT_FIRST_COURSE
                class_info.save()

