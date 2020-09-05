from webapp.models import *
from django.core.management.base import BaseCommand
from classroom.models import VirtualclassInfo, VirtualclassType, ClassInfo, \
    CourseLesson, VirtualclassHomeworkAttachment, VirtualclassResource as NewVirtualclassResource, \
    VirtualclassHomeworkResult, VirtualclassComment, ClassMember
from tutor.models import TutorInfo
from scheduler.models import StudentTimetable
import random
from student.models import UserStudentInfo
from scheduler.models import ScheduleVirtualclassMember, TutorTimetable
from finance.models import BalanceChangeNew as BalanceChange
from webapp.utils import print_insert_table_times
from webapp.new_model_add import CreateTutor, CreateStudent
from webapp.app_settings import START_ID, END_ID


start_id = START_ID
end_id = END_ID


def get_next_session(session):
    try:
        next_session = Session.objects.get(course=session.course, session_no=session.session_no + 1, status='Active')
    except Session.DoesNotExist:
        try:
            course = Course.objects.get(programme=session.course.programme,
                                        course_level=session.course.course_level + 1)
            next_session = Session.objects.filter(course=course, session_no=1, status='Active').first()
        except Course.DoesNotExist:
            return None
    return next_session


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--max_id',
                            dest='max_id',
                            default='')

        parser.add_argument('--term',
                            dest='term',
                            default='gt')

    def get_tutor_info(self, appointment):

        '''通过appointment查询新数据库的老师'''

        hosts = appointment.hosts
        hosts = hosts.first()
        if not hosts:
            return None
        try:
            tutor_user = TutorInfo.objects.filter(username=hosts.username).first()
        except TutorInfo.DoesNotExist:
            create_tutor = CreateTutor(hosts)
            tutor_user = create_tutor.add_tutor()
        return tutor_user

    def get_class_monitor(self, student: User):

        '''
        :param student:   班长
        :return: UserStudentInfo
        '''
        try:
            monitor = UserStudentInfo.objects.filter(parent_user__username=student.username).first()
        except UserStudentInfo.DoesNotExist:
            create_student = CreateStudent(student)
            monitor = create_student.add_student()
        return monitor

    def get_students_info(self, invitees):

        '''通过appointment查询所有学生在新库中的id'''

        students = {}
        for invitee in invitees:
            student_info = UserStudentInfo.objects.filter(parent_user__username=invitee.username).first()
            # student_infos = UserStudentInfo.objects.filter(parent_user__username=invitee.username).all()
            if student_info:
                students[invitee.username] = student_info
            else:
                create_student = CreateStudent(invitee)
                student_info = create_student.add_student()
                if student_info:
                    students[invitee.username] = student_info
        return students

    def set_class_info_level(self, monitor: UserStudentInfo, class_info: ClassInfo):

        '''把班长的进度给班级进度'''

        class_info.course_id = monitor.course_id
        class_info.lesson_no = monitor.lesson_no
        lesson = CourseLesson.objects.filter(course_id=monitor.course_id, lesson_no=monitor.lesson_no, status=CourseLesson.ACTIVE).first()
        class_info.lesson = lesson
        class_info.course_edition_id = monitor.course_edition.id
        class_info.course_level = monitor.course_level
        return class_info

    def create_class_info(self, appointment: Appointment, student_dict):

        monitor = Membership.objects.filter(learning_group=appointment.learning_group, role=Membership.Monitor).first()
        flag = 0
        if monitor:
            monitor = self.get_class_monitor(monitor.group_member)
        else:   # 教室里没有人
            for key, student in student_dict.items():
                if student.id > flag:
                    flag = student.id
                    monitor = student
            class_info = ClassInfo()
            class_info.id = random.randint(start_id, end_id)
            class_info.creator_user = monitor
            class_info.leader_user = monitor
            class_info.class_type_id = ClassType.SMALLCLASS
            class_info.user_num = 0
            class_info.first_course = ClassInfo.NOT_FIRST_COURSE
            class_info.class_name = monitor.real_name
            # class_info.course_id = monitor.course_id
            # class_info.course_edition_id = monitor.course_edition_id
            # class_info.course_level = monitor.course_level
            # class_info.lesson_id = monitor.lesson_id
            # class_info.lesson_no = monitor.lesson_no
            class_info.save()
            return class_info
        # 创建班级
        class_info = ClassInfo.objects.filter(creator_user=monitor).first()
        if class_info:
            return class_info

        class_info = ClassInfo()
        class_info.id = random.randint(start_id, end_id)
        class_info.creator_user = monitor
        class_info.leader_user = monitor
        class_info.class_type_id = ClassType.SMALLCLASS
        class_info.user_num = 0
        class_info.class_name = monitor.real_name
        # class_info.course_id = monitor.course_id
        # class_info.course_edition_id = monitor.course_edition_id
        # class_info.course_level = monitor.course_level
        # class_info.lesson_id = monitor.lesson_id
        # class_info.lesson_no = monitor.lesson_no
        class_info = self.set_class_info_level(monitor, class_info)
        class_info.save()
        # members = Membership.objects.filter(learning_group=appointment.learning_group).all()
        #
        # for member in members:
        #     ng_member = self.get_class_monitor(member.group_member)
        #
        #     class_member = ClassMember()
        #     class_member.class_field = class_info
        #     class_member.student_user = ng_member
        #     if class_info.leader_user_id == ng_member.id:
        #         class_member.role = ClassMember.MONITOR
        #     else:
        #         class_member.role = ClassMember.MEMBER
        #     class_info.user_num = class_info.user_num + 1
        #     class_info.save()
        #     class_member.save()
        return class_info

    def add_scheduler_member_and_timetable(self, vc: VirtualClass, vc_info: VirtualclassInfo, students: dict):
        '''
        根据virtulclass_info生成预约本节课的学生
        :param vc_info:
        :return:
        '''
        if vc_info.class_type_id == ClassType.ONE2ONE:

            student_timetable = StudentTimetable()
            student_timetable.id = random.randint(start_id, end_id)
            student_timetable.tutor_user = vc_info.tutor_user
            student_timetable.class_type = vc_info.class_type
            student_timetable.student_user = vc_info.student_user
            student_timetable.class_field = vc_info.class_field
            student_timetable.start_time = vc_info.start_time
            student_timetable.end_time = vc_info.end_time
            student_timetable.virtual_class = vc_info
            student_timetable.status = StudentTimetable.SUCCESS_APPOINTMENT
            student_timetable.save()

            in_out_time = StudentInOutTime.objects.filter(virtualclass=vc).first()
            vc_member = ScheduleVirtualclassMember()
            vc_member.virtual_class = vc_info
            vc_member.class_field = vc_info.class_field
            vc_member.student_user = vc_info.student_user
            vc_member.start_time = vc_info.start_time
            vc_member.first_course = vc_info.first_course
            if in_out_time:
                vc_member.enter_time = in_out_time.in_class_time
                vc_member.leave_time = in_out_time.out_class_time
            vc_member.student_timetable = student_timetable
            vc_member.class_type_id = vc_info.class_type_id
            vc_member.save()

        else:   # 小班课
            for student_name, student in students.items():
                student_timetable = StudentTimetable()
                student_timetable.id = random.randint(start_id, end_id)
                student_timetable.tutor_user = vc_info.tutor_user
                student_timetable.class_type = vc_info.class_type
                student_timetable.student_user_id = student.id
                student_timetable.class_field = vc_info.class_field
                student_timetable.start_time = vc_info.start_time
                student_timetable.end_time = vc_info.end_time
                student_timetable.virtual_class = vc_info
                student_timetable.status = StudentTimetable.SUCCESS_APPOINTMENT
                student_timetable.save()

                in_out_time = StudentInOutTime.objects.filter(student__username=student_name, virtualclass=vc).first()
                vc_member = ScheduleVirtualclassMember()
                vc_member.virtual_class = vc_info
                vc_member.class_field = vc_info.class_field
                vc_member.student_user_id = student.id
                vc_member.start_time = vc_info.start_time
                vc_member.first_course = 0 if student.student_class_sum else 1
                if in_out_time:
                    vc_member.enter_time = in_out_time.in_class_time
                    vc_member.leave_time = in_out_time.out_class_time
                vc_member.student_timetable = student_timetable
                vc_member.class_type_id = vc_info.class_type_id

                vc_member.save()

    def add_virtualclass_comment(self, vc: VirtualClass, vc_info: VirtualclassInfo, students_dict):
        '''
        添加课后评论
        :param vc:
        :param vc_info:
        :return:
        '''
        # 学生老师评论
        comments = ClassComment.objects.filter(virtual_class=vc).all()
        # 学生老师打分
        evaluations = ClassEvaluation.objects.filter(virtual_class=vc).all()

        invitees = vc.appointment.invitees.all()
        invitees_dict = {}
        for invitee in invitees:
            invitees_dict[invitee.username] = invitee

        student_comments = {}
        tutor_comments = {}
        for comment in comments:

            if comment.user_role == 'Student':  # 老师评语
                student_user = students_dict.get(comment.user.username, None)
                if not student_user:
                    continue
                tutor_comment = VirtualclassComment()
                tutor_comment.virtual_class = vc_info
                tutor_comment.role = VirtualclassComment.TEACHER
                tutor_comment.tutor_user = vc_info.tutor_user
                tutor_comment.role = VirtualclassComment.TEACHER
                tutor_comment.student_user = student_user
                tutor_comment.comment_zh = comment.comment
                tutor_comments[comment.user.username] = tutor_comment
            elif comment.user_role == 'Tutor':   # 学生反馈
                student_user = students_dict.get(comment.commentor.username, None)
                if not student_user:
                    continue
                student_comment = VirtualclassComment()
                student_comment.virtual_class = vc_info
                student_comment.role = VirtualclassComment.STUDENT
                student_comment.comment_zh = comment.comment
                student_comment.tutor_user = vc_info.tutor_user
                student_comment.student_user = students_dict[comment.commentor.username]
                student_comments[comment.commentor.username] = student_comment

        for evaluation in evaluations:
            if evaluation.user_role == 'Student':

                tutor_comment = tutor_comments.get(evaluation.user.username)
                if not tutor_comment:
                    student_user = students_dict.get(evaluation.user.username, None)
                    if not student_user:
                        continue
                    tutor_comment = VirtualclassComment()
                    tutor_comment.virtual_class = vc_info
                    tutor_comment.role = VirtualclassComment.TEACHER
                    tutor_comment.tutor_user = vc_info.tutor_user
                    tutor_comment.student_user = student_user
                    tutor_comments[evaluation.user.username] = tutor_comment
                if evaluation.category == 'PQ':
                    tutor_comment.rating_pk = evaluation.score
                elif evaluation.category == 'SP':
                    tutor_comment.rating_id = evaluation.score
                elif evaluation.category == 'AR':
                    tutor_comment.rating_le = evaluation.score
            else:
                evaluator = evaluation.evaluator

                student_user = students_dict.get(evaluator.username, None)
                if not student_user:
                    continue

                student_comment = student_comments.get(evaluator.username)
                if not student_comment:
                    student_comment = VirtualclassComment()
                    student_comment.role = VirtualclassComment.STUDENT
                    student_comment.virtual_class = vc_info
                    student_comment.tutor_user = vc_info.tutor_user
                    student_comment.student_user = students_dict[evaluator.username]
                    student_comments[evaluator.username] = student_comment
                if evaluation.category == 'PK':
                    student_comment.rating_pk = evaluation.score
                elif evaluation.category == 'ID':
                    student_comment.rating_id = evaluation.score
                elif evaluation.category == 'LE':
                    student_comment.rating_le = evaluation.score

        for key, value in tutor_comments.items():
            value.save()
        for key, value in student_comments.items():
            value.save()

    def add_virtualclass_homework_and_student_balance(self, vc: VirtualClass, vc_info: VirtualclassInfo, student_dict, static_url):
        '''
        添加学生家庭作业跟扣除课时记录
        :param vc:
        :param vc_info:
        :param student_dict:
        :param static_url:
        :return:
        '''
        invitees = vc.appointment.invitees.all()

        invitee_dict = {}

        for invitee in invitees:
            invitee_dict[invitee.username] = invitee

        session = vc.course_session
        if not session:
            return
        for invitee in invitees:
            homeworks = Homework.objects.filter(session=session).all()
            homework_results = HomeworkResult.objects.filter(user=invitee, homework__in=homeworks).all()
            for homework_result in homework_results:
                virtualclass_homework_result = VirtualclassHomeworkResult()
                virtualclass_homework_result.virtual_class = vc_info
                virtualclass_homework_result.homework_id = homework_result.homework_id
                virtualclass_homework_result.student_user = student_dict[invitee.username]
                virtualclass_homework_result.tutor_user = vc_info.tutor_user
                virtualclass_homework_result.score = homework_result.score
                virtualclass_homework_result.comment_zh = homework_result.comment
                virtualclass_homework_result.save()

                # 添加家庭作业附件
                done_homeworks = Donehomework.objects.filter(homeresult=homework_result).all()
                if len(done_homeworks) == 0:
                    virtualclass_homework_result.delete()
                for done_homework in done_homeworks:
                    vc_homework_attachment = VirtualclassHomeworkAttachment()
                    vc_homework_attachment.virtual_class = vc_info
                    vc_homework_attachment.homework_result = virtualclass_homework_result
                    vc_homework_attachment.attachment = static_url + done_homework.result_content
                    vc_homework_attachment.save()

            # 添加本节课课时
            account_balancechanges = AccountBalanceChange.objects.filter(reference=vc.id, user_id=invitee.id).all()
            for balance in account_balancechanges:
                balance_change = BalanceChange()
                # balance_change.id = balance.id
                balance_change.user_id = student_dict[invitee.username].id
                balance_change.reason = balance.reason
                balance_change.role = BalanceChange.CHILDREN
                balance_change.amount = balance.amount
                balance_change.reference = vc_info.id
                balance_change.parent_user_id = student_dict[invitee.username].parent_user_id

                adviser = CourseAdviserStudent.objects.filter(start_time__lte=balance.created_on,
                                                    student_id=balance.user_id).order_by('-start_time').first()
                if adviser:
                    balance_change.adviser_user_id = adviser.cms_user.id
                learn_manager = LearnManagerStudent.objects.filter(start_time__lte=balance.created_on,
                                                   student_id=balance.user_id).order_by('-start_time').first()
                if learn_manager:
                    balance_change.xg_user_id = learn_manager.cms_user.id
                balance_change.create_time = balance.created_on
                balance_change.update_time = balance.updated_on
                balance_change.save()

    def add_tutor_timetable(self, vc: VirtualClass, vc_info: VirtualclassInfo):
        '''
        添加老师课表记录
        :param vc:
        :param vc_info:
        :return:
        '''
        id = random.randint(start_id, end_id)
        tutor_timetable = TutorTimetable()
        tutor_timetable.id = id
        tutor_timetable.tutor_user = vc_info.tutor_user
        tutor_timetable.class_type = vc_info.class_type
        tutor_timetable.student_user = vc_info.student_user
        tutor_timetable.class_field = vc_info.class_field
        tutor_timetable.start_time = vc_info.start_time
        tutor_timetable.end_time = vc_info.end_time
        tutor_timetable.virtual_class = vc_info
        tutor_timetable.status = TutorTimetable.SUCCESS_APPOINTMENT
        tutor_timetable.save()

    def add_tutor_virtualclass_resource(self, vc: VirtualClass, vc_info: VirtualclassInfo):
        '''
        添加上课所用扩展课件
        :param vc:
        :param vc_info:
        :return:
        '''
        vc_resources = VirtualclassResource.objects.filter(virtualclass=vc).all()
        for vc_resource in vc_resources:
            new_vc_resource = NewVirtualclassResource()
            new_vc_resource.virtual_class = vc_info
            new_vc_resource.ext_course_id = vc_resource.ext_course_id
            new_vc_resource.save()

    def add_tutor_balancechange(self, vc: VirtualClass, vc_info: VirtualclassInfo):
        '''
        添加老师上课工资
        :param vc:
        :param vc_info:
        :return:
        '''
        hosts = vc.appointment.hosts.first()
        account_balancechanges = AccountBalanceChange.objects.filter(reference=vc.id, user_id=hosts.id).all()
        for balance in account_balancechanges:
            balance_change = BalanceChange()
            # balance_change.id = balance.id
            balance_change.user_id = vc_info.tutor_user.id
            balance_change.role = BalanceChange.TEACHER
            balance_change.reason = balance.reason
            balance_change.amount = balance.amount
            balance_change.reference = vc_info.id
            balance_change.create_time = vc.created_on
            balance_change.update_time = vc.updated_on
            balance_change.save()

    def add_virtualclass(self, virtualclass, static_url):

        for vc in virtualclass:
            vc_info = VirtualclassInfo()
            vc_info_id = random.randint(start_id, end_id)
            vc_info.id = vc_info_id

            tutor_user = self.get_tutor_info(vc.appointment)
            if not tutor_user:
                logger.error('virtualclass没有老师，vc_id={}'.format(vc.id))
                continue
            vc_info.tutor_user = tutor_user
            if vc.virtualclass_type == 'Agaro':
                vc_info.virtualclass_type_id = VirtualclassType.TK
            else:
                vc_info.virtualclass_type_id = VirtualclassType.TK

            if not vc.class_type_id:
                vc.class_type_id = 1
            vc_info.class_type_id = vc.class_type_id
            invitees = vc.appointment.invitees.all()
            students_dict = self.get_students_info(invitees)

            if not students_dict:
                continue

            if vc.class_type_id == 1:  # 一对一
                vc_info.student_user = list(students_dict.values())[0]
            else:   # 小班课
                # 班长创建教室
                vc_info.class_field = self.create_class_info(vc.appointment, students_dict)
                vc_info.student_user = vc_info.class_field.leader_user

            first_course = False
            for invitee in invitees:
                student_class_sum = AccountBalanceChange.objects.filter(user=invitee, reason=AccountBalanceChange.AD_HOC, updated_on__lt=vc.appointment.scheduled_time).count()
                if student_class_sum is None or student_class_sum == 0:
                    first_course = True
                student = students_dict[invitee.username]
                student.student_class_sum = student_class_sum
            vc_info.first_course = first_course

            vc_info.start_time = vc.appointment.scheduled_time
            vc_info.end_time = vc.appointment.scheduled_time + timedelta(minutes=55)
            vc_info.actual_start_time = vc.actual_start
            vc_info.actual_end_time = vc.actual_end

            if vc.is_delivered and vc.end_reason == 0:  # 正常结束
                vc_info.status = VirtualclassInfo.FINISH_NOMAL
            elif vc.is_delivered and vc.end_reason != 0:
                vc_info.status = VirtualclassInfo.FINISH_ABNOMAL
                vc_info.reason = vc.end_reason
                vc_info.remark = vc.end_reason_description
            elif not vc.is_delivered and vc.appointment.scheduled_time < timezone.now() - timedelta(hours=2):
                vc_info.status = VirtualclassInfo.FINISH_ABNOMAL
                vc_info.reason = VirtualclassInfo.CLASS_NOONE
            else:
                vc_info.status = VirtualclassInfo.NOT_START

            if vc.course_session:
                vc_info.lesson_id = vc.course_session_id
                vc_info.lesson_no = vc.course_session.session_no
            else:
                if vc.class_type_id == 1:  #一对一
                    monitor = Membership.objects.filter(learning_group=vc.appointment.learning_group,
                                                        role=Membership.Monitor).first()
                    monitor_usercourse = UserCourse.objects.filter(is_default=1, user_id=monitor.group_member.id).first()
                    if not monitor_usercourse:
                        continue
                    course_session = Session.objects.filter(status=Session.Active,
                                                            session_no=monitor_usercourse.session_no,
                                                            course=monitor_usercourse.course).first()
                    if course_session:
                        vc_info.lesson_id = course_session.id
                        vc_info.lesson_no = course_session.session_no
                    vc_count = VirtualClass.objects.filter(appointment__scheduled_time__lt=vc.appointment.scheduled_time,
                                                           appointment__scheduled_time__gte=timezone.now(),
                                                           is_delivered=0, appointment__invitees=monitor.group_member).count()
                    for i in range(vc_count):
                        course_session = get_next_session(course_session)
                    if course_session:
                        vc_info.lesson_id = course_session.id
                        vc_info.lesson_no = course_session.session_no

            vc_info.session_id = vc.session_id
            vc_info.tk_class_id = vc.tk_class_id
            vc_info.save()

            self.add_scheduler_member_and_timetable(vc, vc_info, students_dict)

            # 传课后作业，课后评价
            self.add_virtualclass_comment(vc, vc_info, students_dict)

            # 传家庭作业
            self.add_virtualclass_homework_and_student_balance(vc, vc_info, students_dict, static_url)

            # 老师课表
            self.add_tutor_timetable(vc, vc_info)

            # 老师扩展课件
            self.add_tutor_virtualclass_resource(vc, vc_info)

            # 添加老师课时记录
            self.add_tutor_balancechange(vc, vc_info)

    @print_insert_table_times
    def handle(self, *args, **options):

        static_url = settings.MEDIA_URL
        max_id = int(options.get('max_id', 0))
        term = options.get('term', 'gt')
        if term == 'gt':
            virtualclass = VirtualClass.objects.filter(id__gt=max_id).all()
        else:
            virtualclass = VirtualClass.objects.filter(id__lte=max_id).all()
        # if max_id == 0:
        #     virtualclass = VirtualClass.objects.filter(id__gt=max_id).all()
        # else:
        #     virtualclass = VirtualClass.objects.filter(id__lt=max_id).all()
        self.add_virtualclass(virtualclass, static_url)


