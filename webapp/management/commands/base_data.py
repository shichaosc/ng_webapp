from webapp.models import *
from django.core.management.base import BaseCommand
from course.models import CourseLesson, CourseHomework, \
    Courseware as NewCourseware, CourseAssessmentQuestion, CourseExtcourseTag, CourseExtcourse, \
    CourseExtcourseware, CourseExtcourseOptag, CourseEdition, CourseInfo, CourseQuestionnaire, \
    CourseTeacherGuidebook
from common.models import ExchangeRate as CommonExchangeRate, CommonCoupon, CommonBussinessRule, \
    CommonRuleFormula, CommonAmbassadorCode
from django.conf import settings
from finance.models import ClasstypePrice
from webapp.utils import print_insert_table_times
from finance.models import CoursePackage
from tutor.models import UserLevel
import math
import multiprocessing
from django.db import connections
import os
from django.db.models import Max
from webapp.app_settings import CURRENCY_CHOICES


class Command(BaseCommand):


    def add_arguments(self, parser):

        parser.add_argument('--static_url',
                            dest='static_url',
                            default='')

    @print_insert_table_times
    def add_course_edition(self):
        max_id = CourseEdition.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        programmes = Programme.objects.filter(id__gt=max_id).all()
        for programme in programmes:
            course_edition = CourseEdition()
            course_edition.id = programme.id
            course_edition.edition_name = programme.programme_name
            course_edition.description = programme.description
            course_edition.create_time = programme.created_on
            course_edition.update_time = programme.updated_on
            course_edition.save()
        print('course_edition finish')

    @print_insert_table_times
    def add_course_info(self):
        # CourseInfo.objects.all().delete()
        max_id = CourseInfo.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        courses = Course.objects.filter(id__gt=max_id).all()

        for course in courses:
            course_info = CourseInfo()
            course_info.id = course.id
            course_info.course_level = course.course_level
            course_info.course_edition_id = course.programme_id
            course_info.course_name = course.course_name
            course_info.create_time = course.created_on
            course_info.update_time = course.updated_on
            course_info.save()
        print('course_info finish')

    @print_insert_table_times
    def max_session_no(self):
        max_sessions = Session.objects.values('course_id').filter(status=Session.Active).annotate(Max('session_no')).order_by('course_id')
        max_session_dict = {}
        for max_session in max_sessions:
            max_session_dict[max_session['course_id']] = max_session['session_no__max']
        print(max_session_dict)
        return max_session_dict

    @print_insert_table_times
    def add_course_lesson(self):

        max_id = CourseLesson.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        course_sessions = Session.objects.filter(id__gt=max_id).all()
        # session_tk_files = SessionTkFile.objects.all()

        max_sessions = self.max_session_no()

        for course_session in course_sessions:
            lesson = CourseLesson()
            lesson.id = course_session.id
            lesson.course_id = course_session.course_id
            lesson.lesson_no = course_session.session_no
            lesson.status = utils.course_session_status(course_session.status)
            lesson.create_time = course_session.created_on
            lesson.update_time = course_session.updated_on
            if max_sessions[course_session.course_id] == course_session.session_no and lesson.status == CourseLesson.ACTIVE:
                lesson.unit_end = CourseLesson.END
            lesson.save()

            # session_tk_file = session_tk_files.filter(session=course_session).first()
            # if session_tk_file:
            #     lesson_tk_file = TkFile()
            #     lesson_tk_file.lesson = lesson
            #     lesson_tk_file.tk_file_id = session_tk_file.tk_file_id
            #     lesson_tk_file.save()
        print('course_lesson finish')

    @print_insert_table_times
    def add_homework(self, static_url):
        max_id = CourseHomework.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        homeworks = Homework.objects.filter(id__gt=max_id).all()
        for homework in homeworks:
            course_homework = CourseHomework()
            course_homework.id = homework.id
            course_homework.lesson_id = homework.session_id
            course_homework.hw_content = static_url + homework.hw_content
            course_homework.hw_name = homework.hw_content.split('/')[-1]
            course_homework.status = CourseHomework.ACTIVE
            course_homework.create_time = homework.created_on
            course_homework.update_time = homework.updated_on
            course_homework.save()
        print('add_homework finish')

    @print_insert_table_times
    def add_course_courseware(self, static_url):
        max_id = NewCourseware.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        course_wares = Courseware.objects.filter(id__gt=max_id).all()
        for course_ware in course_wares:
            new_course_ware = NewCourseware()
            new_course_ware.id = course_ware.id
            new_course_ware.lesson_id = course_ware.session_id
            new_course_ware.cw_type = utils.course_ware_cwtype(course_ware.cw_type)
            new_course_ware.cw_seq = course_ware.cw_seq
            new_course_ware.cw_url = static_url + course_ware.cw_content
            new_course_ware.cw_name = os.path.split('/')[-1]
            new_course_ware.create_time = course_ware.created_on
            new_course_ware.update_time = course_ware.updated_on

            tk_file = SessionTkFile.objects.filter(session_id=course_ware.session_id).first()

            if tk_file:
                if new_course_ware.cw_seq == 0 and new_course_ware.cw_type != NewCourseware.IMAGE:
                    new_course_ware.tk_file_id = tk_file.tk_file_id

            new_course_ware.save()
        print('add_course_courseware finish')

    @staticmethod
    def insert_courseware(course_wares):
        static_url = settings.MEDIA_URL
        for course_ware in course_wares:
            new_course_ware = NewCourseware()
            new_course_ware.id = course_ware.id
            new_course_ware.lesson_id = course_ware.session_id
            new_course_ware.cw_type = utils.course_ware_cwtype(course_ware.cw_type)
            new_course_ware.cw_seq = course_ware.cw_seq
            new_course_ware.cw_url = static_url + course_ware.cw_content
            new_course_ware.cw_name = os.path.splitext(course_ware.cw_content)[0]
            new_course_ware.save()

    @print_insert_table_times
    def add_course_courseware_async(self):
        course_ware_count = Courseware.objects.all().count()
        NewCourseware.objects.all().delete()

        pools = multiprocessing.Pool(4)

        for i in range(math.ceil(course_ware_count/1000)):
            course_wares = Courseware.objects.all()[i * 1000: (i + 1) * 1000]

            pools.apply_async(self.insert_courseware, (course_wares,))

        pools.close()  # 关闭进程池，关闭后pools不再接收新的请求
        pools.join()  # 等待pools中所有子进程执行完成，必须放在close语句之后
        print('add_course_courseware finish')

    @print_insert_table_times
    def add_courseware_tk_file(self):
        with connections['pplingodb'].cursor() as cursor:
            sql = "select session_id, tk_file_id from course_sessiontkfile"
            cursor.execute(sql)
            rows = cursor.fetchall()
            with connections['lingoace'].cursor() as lingo_cursor:
                for row in rows:
                    lesson_id = row[0]
                    tk_file_id = row[1]
                    sql = "update course_courseware set tk_file_id = {} where lesson_id={} and cw_seq=0 and cw_type!=2".format(tk_file_id, lesson_id)
                    lingo_cursor.execute(sql)
                    connections['lingoace'].commit()

        # max_id = TkFile.objects.aggregate(Max('id'))
        # max_id = max_id.get('id__max', 0)
        # if not max_id:
        #     max_id = 0
        # tk_session_files = SessionTkFile.objects.filter(id__gt=max_id).all()
        # for tk_session_file in tk_session_files:
        #     tk_file = TkFile()
        #     tk_file.id = tk_session_file.id
        #     tk_file.lesson_id = tk_session_file.session_id
        #     tk_file.tk_file_id = tk_session_file.tk_file_id
        #     tk_file.create_time = timezone.now()
        #     tk_file.update_time = timezone.now()
        #     tk_file.save()
        print('add_courseware_tk_file finish')

    @print_insert_table_times
    def add_test_question(self):
        max_id = CourseAssessmentQuestion.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        test_questions = TestQuestion.objects.filter(id__gt=max_id).all()
        for test_question in test_questions:
            course_test_question = CourseAssessmentQuestion()
            course_test_question.id = test_question.id
            course_test_question.course_id = test_question.course_id
            course_test_question.question_no = test_question.question_id
            course_test_question.degree_of_difficulty = test_question.degree_of_difficulty
            course_test_question.status = utils.test_question_status(test_question.status)
            course_test_question.detail = utils.reg_testquestion_detail(test_question.detail)
            course_test_question.create_time = test_question.created_on
            course_test_question.update_time = test_question.updated_on
            course_test_question.save()
        print('add_test_question finish')

    @print_insert_table_times
    def add_ext_course_tag(self):
        max_id = CourseExtcourseTag.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        ext_course_tags = ExtCourseTag.objects.filter(id__gt=max_id).all()
        for tag in ext_course_tags:
            ext_course_tag = CourseExtcourseTag()
            ext_course_tag.id = tag.id
            ext_course_tag.tag = tag.text
            ext_course_tag.ext_course_type = tag.get_ext_course_type_display()
            ext_course_tag.create_time = timezone.now()
            ext_course_tag.update_time = timezone.now()
            ext_course_tag.save()
        print('add_ext_course_tag finish')

    @print_insert_table_times
    def add_ext_course(self):
        max_id = CourseExtcourse.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        ext_courses = ExtCourse.objects.filter(id__gt=max_id).all()
        for ext_course in ext_courses:
            course_extcourse = CourseExtcourse()
            course_extcourse.id = ext_course.id
            course_extcourse.ext_course_name = ext_course.ext_course_name
            course_extcourse.ext_course_tag_id = ext_course.ext_course_tag_id
            course_extcourse.ext_course_status = ext_course.get_ext_course_status_display()
            course_extcourse.ext_course_type = ext_course.get_ext_course_type_display()
            course_extcourse.ext_course_active = ext_course.get_ext_course_active_display()
            course_extcourse.ext_course_id = ext_course.ext_course_id
            # course_extcourse.tk_file_id = ext_course.tk_ext_id
            course_extcourse.create_time = ext_course.created_on
            course_extcourse.update_time = ext_course.updated_on
            course_extcourse.save()
        print('add_ext_course finish')

    @staticmethod
    def insert_ext_courseware(ext_coursewares):
        print("qi dong jing cheng")
        static_url = settings.MEDIA_URL
        for ext_courseware in ext_coursewares:
            course_extcourseware = CourseExtcourseware()
            course_extcourseware.id = ext_courseware.id
            course_extcourseware.ext_course_id = ext_courseware.ext_course_id
            course_extcourseware.ecw_type = ext_courseware.get_ecw_type_display()
            course_extcourseware.ecw_seq = ext_courseware.ecw_seq
            course_extcourseware.ecw_content = static_url + ext_courseware.ecw_content
            course_extcourseware.save()

    @print_insert_table_times
    def add_ext_courseware_async(self):
        CourseExtcourseware.objects.all().delete()
        ext_coursewares_length = ExtCourseware.objects.all().count()

        # pools = ProcessPool(self.insert_ext_courseware)
        pools = multiprocessing.Pool(4)

        for i in range(math.ceil(ext_coursewares_length/1000)):
            ext_coursewares = ExtCourseware.objects.all()[i * 1000: (i + 1) * 1000]

            pools.apply_async(self.insert_ext_courseware, (ext_coursewares, ))

        pools.close()  # 关闭进程池，关闭后pools不再接收新的请求
        pools.join()  # 等待pools中所有子进程执行完成，必须放在close语句之后

    @print_insert_table_times
    def add_ext_courseware(self, static_url):
        max_id = CourseExtcourseware.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        ext_coursewares = ExtCourseware.objects.filter(id__gt=max_id).all()
        for ext_courseware in ext_coursewares:
            course_extcourseware = CourseExtcourseware()
            course_extcourseware.id = ext_courseware.id
            course_extcourseware.ext_course_id = ext_courseware.ext_course_id
            course_extcourseware.ecw_type = ext_courseware.get_ecw_type_display()
            course_extcourseware.ecw_seq = ext_courseware.ecw_seq
            course_extcourseware.ecw_url = static_url + ext_courseware.ecw_content
            if ext_courseware.ecw_seq == 0 and ext_courseware.ecw_type != CourseExtcourseware.IMAGE:
                course_extcourseware.tk_file_id = ext_courseware.ext_course.tk_ext_id
            course_extcourseware.create_time = ext_courseware.created_on
            course_extcourseware.update_time = ext_courseware.updated_on
            course_extcourseware.save()
        print('add_ext_courseware finish')

    @print_insert_table_times
    def add_ext_course_optag(self):
        max_id = CourseExtcourseOptag.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        ext_course_optags = ExtCourseOpTag.objects.filter(id__gt=max_id).all()
        for ext_course_optag in ext_course_optags:
            course_ext_optag = CourseExtcourseOptag()
            course_ext_optag.id = ext_course_optag.id
            course_ext_optag.ext_course_id = ext_course_optag.ext_course_id
            course_ext_optag.ext_course_tag_id = ext_course_optag.ext_course_op_tag_id
            course_ext_optag.create_time = timezone.now()
            course_ext_optag.update_time = timezone.now()
            course_ext_optag.save()
        print('add_ext_course_optag finish')

    @print_insert_table_times
    def add_parent_question(self):
        max_id = CourseQuestionnaire.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        if max_id > 0:
            return

        with connections['lingoace'].cursor() as cursor:
            cursor.execute('''
            INSERT INTO `course_questionnaire`
VALUES
	( 6, 30102001, '5、孩子的年龄?', '5.How old is your child? \r\n', '{\"no\": \"30102001 \", \"title_zh\": \"5\\u3001\\u5b69\\u5b50\\u7684\\u5e74\\u9f84?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"content\": \"5-7 \\u5c81\", \"score\": \"1\", \"type\": \"text\", \"content_en\": \"5~7 years old\"}}, {\"id\": \"B\", \"detail\": {\"content\": \"8-10 \\u5c81\", \"score\": \"2\", \"type\": \"text\", \"content_en\": \"8-10 years old\"}}, {\"id\": \"C\", \"detail\": {\"content\": \"11-13 \\u5c81\", \"score\": \"3\", \"type\": \"text\", \"content_en\": \"11~13 years old\"}}, {\"id\": \"D\", \"detail\": {\"content\": \"14-15 \\u5c81\", \"score\": \"4\", \"type\": \"text\", \"content_en\": \"14~15 years old\"}}, {\"id\": \"E\", \"detail\": {\"content\": \"\", \"score\": \"\", \"type\": \"text\", \"content_en\": \"\"}}, {\"id\": \"F\", \"detail\": {\"content\": \"\", \"score\": \"\", \"type\": \"text\", \"content_en\": \"\"}}], \"title_en\": \"5.How old is your child? \\r\\n\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 7, 30102002, '6、孩子之前学过中文吗?(如果学过)学习中文多长时间?', '6.Have your child learned Chinese before? (If learned) How long have your child learned? \r\n', '{\"alternatives\": [{\"detail\": {\"score\": \"1\", \"content_en\": \"Haven\'t learned &learned Chinese about 1 year\", \"content\": \"\\u6ca1\\u6709\\uff0c\\u6216\\u8005\\u5b66\\u4e60\\u4e2d\\u6587 1 \\u5b66\\u5e74\\u5de6\\u53f3\", \"type\": \"text\"}, \"id\": \"A\"}, {\"detail\": {\"score\": \"1\", \"content_en\": \"learned Chinese about 2 years\", \"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u6587 2 \\u5b66\\u5e74\\u5de6\\u53f3 \", \"type\": \"text\"}, \"id\": \"B\"}, {\"detail\": {\"score\": \"1\", \"content_en\": \"learned Chinese about 3 years\", \"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u6587 3 \\u5b66\\u5e74\\u5de6\\u53f3\", \"type\": \"text\"}, \"id\": \"C\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \"learned Chinese about 4 years \", \"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u6587 4 \\u5b66\\u5e74\\u5de6\\u53f3\", \"type\": \"text\"}, \"id\": \"D\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \"learned Chinese about 5 years &more than 5years \", \"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u6587 5 \\u5b66\\u5e74\\u6216 5 \\u5b66\\u5e74\\u4ee5\\u4e0a\", \"type\": \"text\"}, \"id\": \"E\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"F\"}], \"no\": \"30102002 \", \"title_zh\": \"6\\u3001\\u5b69\\u5b50\\u4e4b\\u524d\\u5b66\\u8fc7\\u4e2d\\u6587\\u5417?(\\u5982\\u679c\\u5b66\\u8fc7)\\u5b66\\u4e60\\u4e2d\\u6587\\u591a\\u957f\\u65f6\\u95f4?\", \"title_en\": \"6.Have your child learned Chinese before? (If learned) How long have your child learned? \\r\\n\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 11, 30103001, '5、孩子的年龄？', '5.How old is your child?', '{\"no\": \"30103001\", \"title_zh\": \"5\\u3001\\u5b69\\u5b50\\u7684\\u5e74\\u9f84\\uff1f\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"content\": \"6~8\\u5c81\", \"score\": \"1\", \"type\": \"text\", \"content_en\": \"6~8 years old\"}}, {\"id\": \"B\", \"detail\": {\"content\": \"8~10\\u5c81\", \"score\": \"2\", \"type\": \"text\", \"content_en\": \"8~10 years old\"}}, {\"id\": \"C\", \"detail\": {\"content\": \"10~12\\u5c81\", \"score\": \"3\", \"type\": \"text\", \"content_en\": \"10~12 years old\"}}, {\"id\": \"D\", \"detail\": {\"content\": \"12~15\\u5c81\", \"score\": \"4\", \"type\": \"text\", \"content_en\": \"12~15 years old\"}}, {\"id\": \"E\", \"detail\": {\"content\": \"15~18\\u5c81\", \"score\": \"5\", \"type\": \"text\", \"content_en\": \"More than15 years old\"}}, {\"id\": \"F\", \"detail\": {\"content\": \"\", \"score\": \"5\", \"type\": \"text\", \"content_en\": \"\"}}], \"title_en\": \"5.How old is your child?\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 12, 30103002, '6、孩子之前学过中文吗？（如果学过）学习中文多长时间', '6.Have your child learned Chinese before? (If learned) How long have your child learned? ', '{\"no\": \"30103002\", \"title_zh\": \"6\\u3001\\u5b69\\u5b50\\u4e4b\\u524d\\u5b66\\u8fc7\\u4e2d\\u6587\\u5417\\uff1f\\uff08\\u5982\\u679c\\u5b66\\u8fc7\\uff09\\u5b66\\u4e60\\u4e2d\\u6587\\u591a\\u957f\\u65f6\\u95f4\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"content\": \"\\u6ca1\\u6709\\uff0c\\u6216\\u8005\\u5b66\\u4e60\\u5b66\\u4e2d\\u65870~1\\u5b66\\u5e74\", \"score\": \"1\", \"type\": \"text\", \"content_en\": \"Haven\'t learned or learned Chinese 0~1 year\"}}, {\"id\": \"B\", \"detail\": {\"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u65871~2\\u5b66\\u5e74\", \"score\": \"2\", \"type\": \"text\", \"content_en\": \"learned Chinese 1~2 years\"}}, {\"id\": \"C\", \"detail\": {\"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u65872~3\\u5b66\\u5e74\", \"score\": \"3\", \"type\": \"text\", \"content_en\": \"learned Chinese 2~3 years\"}}, {\"id\": \"D\", \"detail\": {\"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u65873~4\\u5b66\\u5e74\", \"score\": \"4\", \"type\": \"text\", \"content_en\": \"learned Chinese 3~4 years\"}}, {\"id\": \"E\", \"detail\": {\"content\": \"\\u5b66\\u8fc7\\uff0c\\u5b66\\u4e2d\\u65875\\u5b66\\u5e74\\u4ee5\\u4e0a\", \"score\": \"5\", \"type\": \"text\", \"content_en\": \"learned Chinese 5 years or more than 5 years\"}}, {\"id\": \"F\", \"detail\": {\"content\": \"\", \"score\": \"5\", \"type\": \"text\", \"content_en\": \"\"}}], \"title_en\": \"6.Have your child learned Chinese before? (If learned) How long have your child learned? \"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 14, 30103003, '7、孩子每周花多长时间学习中文?\r\n', '7.How long does your child usually spend on learning Chinese? \r\n', '{\"alternatives\": [{\"detail\": {\"content\": \"\\u5b66\\u751f\\u6ca1\\u6709\\u5b66\\u8fc7\\u4e2d\\u6587(\\u6216\\u751f\\u6d3b\\u4e2d\\u63a5\\u89e6\\u8fc7\\u4e00\\u70b9\\u4e2d\\u6587) \", \"type\": \"text\", \"score\": \"1\", \"content_en\": \"Doesn\'t learn Chinese\"}, \"id\": \"A\"}, {\"detail\": {\"content\": \"\\u4e00\\u5468 0-1 \\u5c0f\\u65f6\", \"type\": \"text\", \"score\": \"2\", \"content_en\": \"0~1 hour a week\"}, \"id\": \"B\"}, {\"detail\": {\"content\": \"\\u4e00\\u5468 1-2 \\u5c0f\\u65f6\", \"type\": \"text\", \"score\": \"3\", \"content_en\": \"1~2 hours a week \"}, \"id\": \"C\"}, {\"detail\": {\"content\": \"\\u4e00\\u5468 2-3 \\u5c0f\\u65f6\", \"type\": \"text\", \"score\": \"4\", \"content_en\": \"2~3 hours a week\"}, \"id\": \"D\"}, {\"detail\": {\"content\": \"\\u4e00\\u5468 4 \\u5c0f\\u65f6\\u53ca\\u4ee5\\u4e0a\", \"type\": \"text\", \"score\": \"5\", \"content_en\": \"At least 4 hours\"}, \"id\": \"E\"}, {\"detail\": {\"content\": \"\", \"type\": \"text\", \"score\": \"5\", \"content_en\": \"\"}, \"id\": \"F\"}], \"title_zh\": \"7\\u3001\\u5b69\\u5b50\\u6bcf\\u5468\\u82b1\\u591a\\u957f\\u65f6\\u95f4\\u5b66\\u4e60\\u4e2d\\u6587?\\r\\n\", \"no\": \"30103003\", \"title_en\": \"7.How long does your child usually spend on learning Chinese? \\r\\n\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 15, 30103004, '8、孩子的中文“听说”技能评分最符合下面哪个? ', '8.How is your child\'s Chinese listening and speaking skills? (From low to high) \r\n', '{\"no\": \"30103004\", \"title_zh\": \"8\\u3001\\u5b69\\u5b50\\u7684\\u4e2d\\u6587\\u201c\\u542c\\u8bf4\\u201d\\u6280\\u80fd\\u8bc4\\u5206\\u6700\\u7b26\\u5408\\u4e0b\\u9762\\u54ea\\u4e2a? \", \"alternatives\": [{\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"1\", \"content\": \"/media/exambank/30103004A-1.png\"}, \"id\": \"A\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"2\", \"content\": \"/media/exambank/30103004B-1.png\"}, \"id\": \"B\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"3\", \"content\": \"/media/exambank/30103004C-1.png\"}, \"id\": \"C\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"4\", \"content\": \"/media/exambank/30103004D-1.png\"}, \"id\": \"D\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"5\", \"content\": \"/media/exambank/30103004E-1.png\"}, \"id\": \"E\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"text\", \"score\": \"\", \"content\": \"\"}, \"id\": \"F\"}], \"title_en\": \"8.How is your child\'s Chinese listening and speaking skills? (From low to high) \\r\\n\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 16, 30103005, '9、孩子的中文“读写”技能评分最符合下面哪个? ', '9.How is your child\'s Chinese reading and writing skills? (From low to high) \r\n', '{\"no\": \"30103005\", \"title_zh\": \"9\\u3001\\u5b69\\u5b50\\u7684\\u4e2d\\u6587\\u201c\\u8bfb\\u5199\\u201d\\u6280\\u80fd\\u8bc4\\u5206\\u6700\\u7b26\\u5408\\u4e0b\\u9762\\u54ea\\u4e2a? \", \"alternatives\": [{\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"1\", \"content\": \"/media/exambank/30103005A-1.png\"}, \"id\": \"A\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"2\", \"content\": \"/media/exambank/30103005B-1.png\"}, \"id\": \"B\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"3\", \"content\": \"/media/exambank/30103005C-1.png\"}, \"id\": \"C\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"4\", \"content\": \"/media/exambank/30103005D-1.png\"}, \"id\": \"D\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"image\", \"score\": \"5\", \"content\": \"/media/exambank/30103005E-1.png\"}, \"id\": \"E\"}, {\"detail\": {\"content_en\": \"\", \"type\": \"text\", \"score\": \"\", \"content\": \"\"}, \"id\": \"F\"}], \"title_en\": \"9.How is your child\'s Chinese reading and writing skills? (From low to high) \\r\\n\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 17, 30103006, '10、孩子在家说什么语言?', '10.What kind of language does your child speak at home?', '{\"title_zh\": \"10\\u3001\\u5b69\\u5b50\\u5728\\u5bb6\\u8bf4\\u4ec0\\u4e48\\u8bed\\u8a00?\", \"no\": \"30103006\", \"title_en\": \"10.What kind of language does your child speak at home?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"score\": \"1\", \"content\": \"\\u5728\\u5bb6\\u4ece\\u6765\\u4e0d\\u8bf4\\u4e2d\\u6587\\uff0c\\u5b69\\u5b50\\u4e5f\\u4ece\\u6765\\u6ca1\\u6709\\u63a5\\u89e6\\u8fc7\\u4e2d\\u6587\", \"content_en\": \"doesn\'t speak Chinese at home\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"score\": \"2\", \"content\": \"\\u5728\\u5bb6\\u4e0d\\u8bf4\\u4e2d\\u6587\\uff0c\\u4f46\\u662f\\u5b69\\u5b50\\u5728\\u5176\\u4ed6\\u5730\\u65b9\\u53ef\\u4ee5\\u63a5\\u89e6\\u5230\\u4e2d\\u6587\", \"content_en\": \"doesn\'t speak Chinese at home but can get access to Chinese. (With neighbors, relatives or friends)\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"score\": \"3\", \"content\": \"\\u5728\\u5bb6\\u5b69\\u5b50\\u80fd\\u7528\\u4e2d\\u6587\\u7ec3\\u4e60\\u4e00\\u4e9b\\u8bcd\\u8bed\\uff0c\\u4f46\\u5927\\u90e8\\u5206\\u65f6\\u95f4\\u4e0d\\u8bf4 \", \"content_en\": \"can speak a little Chinese at home\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"score\": \"4\", \"content\": \"\\u7236\\u6bcd\\u4e2d\\u6709\\u4e00\\u4e2a\\u8bf4\\u4e2d\\u6587\\u53e6\\u4e00\\u4e2a\\u8bf4\\u522b\\u7684\\u8bed\\u8a00\", \"content_en\": \"one of the parents speaks another language\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"score\": \"5\", \"content\": \"\\u4e2d\\u6587\\u662f\\u5bb6\\u91cc\\u7684\\u57fa\\u7840\\u8bed\\u8a00\", \"content_en\": \" Chinese is the basic language\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"score\": \"\", \"content\": \"\", \"content_en\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 18, 30102003, '7、孩子每周花多长时间学习中文?', '7.How long does your child usually spend on learning Chinese? ', '{\"alternatives\": [{\"detail\": {\"score\": \"1\", \"content_en\": \" 0~1 hours a week\", \"content\": \"\\u4e00\\u5468 0~1 \\u5c0f\\u65f6\", \"type\": \"text\"}, \"id\": \"A\"}, {\"detail\": {\"score\": \"1\", \"content_en\": \"1~2 hours a week \", \"content\": \"\\u4e00\\u5468 1~2 \\u5c0f\\u65f6\", \"type\": \"text\"}, \"id\": \"B\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \"2~3 hours a week\", \"content\": \"\\u4e00\\u5468 2~3 \\u5c0f\\u65f6\", \"type\": \"text\"}, \"id\": \"C\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \"4~5 hours a week\", \"content\": \"\\u4e00\\u5468 4 ~5\\u5c0f\\u65f6\", \"type\": \"text\"}, \"id\": \"D\"}, {\"detail\": {\"score\": \"4\", \"content_en\": \"At least 6 hours\", \"content\": \"\\u4e00\\u5468 6 \\u5c0f\\u65f6\\u53ca\\u4ee5\\u4e0a\", \"type\": \"text\"}, \"id\": \"E\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"F\"}], \"no\": \"30102003\", \"title_zh\": \"7\\u3001\\u5b69\\u5b50\\u6bcf\\u5468\\u82b1\\u591a\\u957f\\u65f6\\u95f4\\u5b66\\u4e60\\u4e2d\\u6587?\", \"title_en\": \"7.How long does your child usually spend on learning Chinese? \"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 19, 30102004, '8、孩子认识拼音吗?', '8.Have your child learned Chinese Pinyin?', '{\"alternatives\": [{\"detail\": {\"score\": \"0\", \"content_en\": \"Haven\'t learned Pinyin\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u61c2\", \"type\": \"text\"}, \"id\": \"A\"}, {\"detail\": {\"score\": \"1\", \"content_en\": \" Can spell and read Pinyin\", \"content\": \"\\u80fd\\u62fc\\u8bfb\", \"type\": \"text\"}, \"id\": \"B\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"C\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"D\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"E\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"F\"}], \"no\": \"30102004\", \"title_zh\": \"8\\u3001\\u5b69\\u5b50\\u8ba4\\u8bc6\\u62fc\\u97f3\\u5417?\", \"title_en\": \"8.Have your child learned Chinese Pinyin?\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 20, 30102005, '9、孩子的阅读水平怎么样?(不加拼音) ', '9.How is your child\'s Chinese reading skills?(without Pinyin)', '{\"alternatives\": [{\"detail\": {\"score\": \"1\", \"content_en\": \" Can not read any Chinese characters\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u8ba4\\u8bc6\\u6c49\\u5b57\", \"type\": \"text\"}, \"id\": \"A\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \"Can read simple words and sentences\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"type\": \"text\"}, \"id\": \"B\"}, {\"detail\": {\"score\": \"3\", \"content_en\": \" Can read simple picture books\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u7ed8\\u672c\", \"type\": \"text\"}, \"id\": \"C\"}, {\"detail\": {\"score\": \"3\", \"content_en\": \" Can read simple stories\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u5c0f\\u6545\\u4e8b\", \"type\": \"text\"}, \"id\": \"D\"}, {\"detail\": {\"score\": \"5\", \"content_en\": \"Can read novel, such as history, science, biography, etc.\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u5c0f\\u8bf4\\uff0c\\u4f8b\\u5982\\u5386\\u53f2\\u3001\\u79d1\\u5b66\\u3001\\u4f20\\u8bb0\\u7b49\", \"type\": \"text\"}, \"id\": \"E\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"F\"}], \"no\": \"30102005\", \"title_zh\": \"9\\u3001\\u5b69\\u5b50\\u7684\\u9605\\u8bfb\\u6c34\\u5e73\\u600e\\u4e48\\u6837?(\\u4e0d\\u52a0\\u62fc\\u97f3) \", \"title_en\": \"9.How is your child\'s Chinese reading skills?(without Pinyin)\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 21, 30102006, '10、孩子的书写水平怎么样? ', '10.How is your child\'s Chinese writing skills?', '{\"alternatives\": [{\"detail\": {\"score\": \"1\", \"content_en\": \"Can not write any Chinese characters\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u4f1a\\u4e66\\u5199\\u6c49\\u5b57\", \"type\": \"text\"}, \"id\": \"A\"}, {\"detail\": {\"score\": \"2\", \"content_en\": \" Can write simple words and sentences\", \"content\": \"\\u80fd\\u591f\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"type\": \"text\"}, \"id\": \"B\"}, {\"detail\": {\"score\": \"3\", \"content_en\": \"Can write a simple paragraph independently\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u4e00\\u6bb5\\u8bdd\", \"type\": \"text\"}, \"id\": \"C\"}, {\"detail\": {\"score\": \"4\", \"content_en\": \"Can write simple stories independently\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u5c0f\\u6545\\u4e8b\", \"type\": \"text\"}, \"id\": \"D\"}, {\"detail\": {\"score\": \"5\", \"content_en\": \"Can write a complete essay independently\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u5b8c\\u6574\\u7684\\u4e00\\u7bc7\\u6587\\u7ae0\", \"type\": \"text\"}, \"id\": \"E\"}, {\"detail\": {\"score\": \"\", \"content_en\": \"\", \"content\": \"\", \"type\": \"text\"}, \"id\": \"F\"}], \"no\": \"30102006\", \"title_zh\": \"10\\u3001\\u5b69\\u5b50\\u7684\\u4e66\\u5199\\u6c34\\u5e73\\u600e\\u4e48\\u6837? \", \"title_en\": \"10.How is your child\'s Chinese writing skills?\"}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 22, 5, '1234', '', '{\"no\": \"5\", \"title_zh\": \"1234\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 40, 30101204, '孩子的年龄?', 'How old is the child？', '{\"no\": \"30101204\", \"title_zh\": \"\\u5b69\\u5b50\\u7684\\u5e74\\u9f84?\", \"title_en\": \"How old is the child\\uff1f\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"5~7\\u5c81\", \"content_en\": \"5~7 years old\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"8~10\\u5c81\", \"content_en\": \"8~10 years old\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"11~13\\u5c81\", \"content_en\": \"11~13 years old\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"14~15\\u5c81\", \"content_en\": \"14~15 years old\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 41, 30101205, '孩子目前的中文听说能力怎么样？', 'How is the child\'s current Chinese listening and speaking ability', '{\"no\": \"30101205\", \"title_zh\": \"\\u5b69\\u5b50\\u76ee\\u524d\\u7684\\u4e2d\\u6587\\u542c\\u8bf4\\u80fd\\u529b\\u600e\\u4e48\\u6837\\uff1f\", \"title_en\": \"How is the child\'s current Chinese listening and speaking ability\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u542c\\u4e0d\\u61c2\\u6216\\u80fd\\u542c\\u61c2\\u6700\\u7b80\\u5355\\u7684\\u4e2d\\u6587\\uff0c\\u4f46\\u4e0d\\u4f1a\\u8bf4\", \"content_en\": \"Can\'t understand Chinese (or just understand the simplest Chinese), can\'t speak Chinese at all\", \"score\": \"1\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u542c\\u61c2\\u5e38\\u7528\\u7684\\u4e2d\\u6587\\uff0c\\u4f46\\u4e0d\\u4f1a\\u8bf4\\u5b8c\\u6574\\u7684\\u4e2d\\u6587\\u53e5\\u5b50\\uff08\\u53ea\\u4f1a\\u8e66\\u8bcd\\u6216\\u4e2d\\u6587\\u4e2d\\u5939\\u6742\\u7740\\u6bcd\\u8bed\\u5355\\u8bcd\\uff09\", \"content_en\": \"Can understand common Chinese, but can\'t speak complete Chinese sentences (always skipping words or with native words)\", \"score\": \"2\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u7528\\u4e2d\\u6587\\u8fdb\\u884c\\u65e5\\u5e38\\u4ea4\\u9645\\uff0c\\u4f1a\\u81ea\\u7136\\u4f7f\\u7528\\u5b8c\\u6574\\u7684\\u53e5\\u5b50\\uff0c\\u4e14\\u7b26\\u5408\\u4e2d\\u6587\\u903b\\u8f91\", \"content_en\": \"Can use Chinese for daily communication, can use complete sentences, and conform to Chinese grammatical logic\", \"score\": \"3\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5728\\u7eaf\\u4e2d\\u6587\\u73af\\u5883\\u4e0b\\uff0c\\u53ef\\u4ee5\\u81ea\\u7531\\u6d41\\u7545\\u5730\\u6c9f\\u901a\", \"content_en\": \"Ability to communicate with others fluently in Chinese in a pure Chinese language environment\", \"score\": \"4\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 42, 31101205, '孩子目前的中文阅读水平怎么样?(不加拼音)', 'How is the child\'s current Chinese reading level? (without Pinyin)', '{\"no\": \"31101205\", \"title_zh\": \"\\u5b69\\u5b50\\u76ee\\u524d\\u7684\\u4e2d\\u6587\\u9605\\u8bfb\\u6c34\\u5e73\\u600e\\u4e48\\u6837?(\\u4e0d\\u52a0\\u62fc\\u97f3)\", \"title_en\": \"How is the child\'s current Chinese reading level? (without Pinyin)\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u8ba4\\u8bc6\\u6c49\\u5b57\", \"content_en\": \"Completely ignorant of Chinese characters\", \"score\": \"1\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"content_en\": \"Ability to read simple Chinese words and sentences\", \"score\": \"2\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u4e2d\\u6587\\u7ed8\\u672c\", \"content_en\": \"Ability to read simple Chinese picture books\", \"score\": \"3\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u4e00\\u822c\\u7684\\u4e2d\\u6587\\u6545\\u4e8b\", \"content_en\": \"Ability to read general Chinese story books\", \"score\": \"3\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u5c0f\\u8bf4\\uff0c\\u4f8b\\u5982\\u5386\\u53f2\\u3001\\u79d1\\u5b66\\u3001\\u4f20\\u8bb0\\u7b49\", \"content_en\": \"Ability to read Chinese fiction, such as history, science, biography, etc\", \"score\": \"5\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 43, 31101204, '\r\n孩子的年龄?', 'How old is the child?', '{\"no\": \"31101204\", \"title_zh\": \"\\r\\n\\u5b69\\u5b50\\u7684\\u5e74\\u9f84?\", \"title_en\": \"How old is the child?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"5~7 \\u5c81\", \"content_en\": \"5~7 years old\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"8~10 \\u5c81\", \"content_en\": \"8~10 years old\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"11~13 \\u5c81\", \"content_en\": \"11~13 years old\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"14~15 \\u5c81\", \"content_en\": \"14~15 years old\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 44, 31101206, '孩子目前的中文书写水平怎么样?', 'How is the child\'s current Chinese writing level?', '{\"no\": \"31101206\", \"title_zh\": \"\\u5b69\\u5b50\\u76ee\\u524d\\u7684\\u4e2d\\u6587\\u4e66\\u5199\\u6c34\\u5e73\\u600e\\u4e48\\u6837?\", \"title_en\": \"How is the child\'s current Chinese writing level?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u4f1a\\u4e66\\u5199\\u6c49\\u5b57\", \"content_en\": \"Can\'t write Chinese characters at all\", \"score\": \"1\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"content_en\": \"Ability to write simple words and sentences\", \"score\": \"2\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u4e00\\u6bb5\\u8bdd\", \"content_en\": \"Ability to write a simple paragraph independently\", \"score\": \"3\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u4e2d\\u6587\\u77ed\\u6587\", \"content_en\": \"Ability to write simple Chinese essays independently\", \"score\": \"4\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u5b8c\\u6574\\u7684\\u4e00\\u7bc7\\u6587\\u7ae0\\uff0c\\u5e76\\u53ef\\u4ee5\\u4f7f\\u7528\\u6210\\u8bed\\u53ca\\u591a\\u6837\\u5316\\u7684\\u4fee\\u8f9e\\u624b\\u6cd5\", \"content_en\": \"Ability to write a complete article independently and to use idioms and various rhetorical devices\", \"score\": \"5\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 45, 32101204, '孩子的中文阅读水平怎么样?(不加拼音)', 'How is the child\'s current Chinese reading level? (without Pinyin)', '{\"no\": \"32101204\", \"title_zh\": \"\\u5b69\\u5b50\\u7684\\u4e2d\\u6587\\u9605\\u8bfb\\u6c34\\u5e73\\u600e\\u4e48\\u6837?(\\u4e0d\\u52a0\\u62fc\\u97f3)\", \"title_en\": \"How is the child\'s current Chinese reading level? (without Pinyin)\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u8ba4\\u8bc6\\u6c49\\u5b57\", \"content_en\": \"Completely ignorant of Chinese characters\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"content_en\": \"Ability to read simple Chinese words and sentences\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u7b80\\u5355\\u7684\\u4e2d\\u6587\\u7ed8\\u672c\", \"content_en\": \"Ability to read simple Chinese picture books\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u4e00\\u822c\\u7684\\u4e2d\\u6587\\u6545\\u4e8b\", \"content_en\": \"Ability to read general Chinese story books\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u9605\\u8bfb\\u5c0f\\u8bf4\\uff0c\\u4f8b\\u5982\\u5386\\u53f2\\u3001\\u79d1\\u5b66\\u3001\\u4f20\\u8bb0\\u7b49\", \"content_en\": \"Ability to read Chinese fiction, such as history, science, biography, etc\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 46, 32101205, '孩子的中文书写水平怎么样?', 'How is the child\'s current Chinese writing level?', '{\"no\": \"32101205\", \"title_zh\": \"\\u5b69\\u5b50\\u7684\\u4e2d\\u6587\\u4e66\\u5199\\u6c34\\u5e73\\u600e\\u4e48\\u6837?\", \"title_en\": \"How is the child\'s current Chinese writing level?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5b8c\\u5168\\u4e0d\\u4f1a\\u4e66\\u5199\\u6c49\\u5b57\", \"content_en\": \"Absolutely unable to write any Chinese characters\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u8bcd\\u8bed\\u548c\\u53e5\\u5b50\", \"content_en\": \"Ability to write simple Chinese words and sentences\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u4e00\\u6bb5\\u8bdd\", \"content_en\": \"Ability to write a simple Chinese paragraph independently\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u7b80\\u5355\\u7684\\u4e2d\\u6587\\u77ed\\u6587\", \"content_en\": \"Ability to write simple Chinese essays independently\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u591f\\u72ec\\u7acb\\u4e66\\u5199\\u5b8c\\u6574\\u7684\\u4e00\\u7bc7\\u6587\\u7ae0\\uff0c\\u5e76\\u53ef\\u4ee5\\u4f7f\\u7528\\u6210\\u8bed\\u53ca\\u591a\\u6837\\u5316\\u7684\\u4fee\\u8f9e\\u624b\\u6cd5\", \"content_en\": \"Ability to write a complete Chinese article independently\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 47, 32101206, '孩子学校目前在学哪一课?', '', '{\"no\": \"32101206\", \"title_zh\": \"\\u5b69\\u5b50\\u5b66\\u6821\\u76ee\\u524d\\u5728\\u5b66\\u54ea\\u4e00\\u8bfe?\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 49, 33101142, '孩子目前的中文水平如何？', 'How is the child\'s current Chinese level?', '{\"no\": \"33101142\", \"title_zh\": \"\\u5b69\\u5b50\\u76ee\\u524d\\u7684\\u4e2d\\u6587\\u6c34\\u5e73\\u5982\\u4f55\\uff1f\", \"title_en\": \"How is the child\'s current Chinese level?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u4e0d\\u80fd\\u4f7f\\u2f64\\u4e2d\\u2f42\\u8fdb\\u2f8f\\u2f47\\u5e38\\u4ea4\\u6d41\", \"content_en\": \"Can\'t communicate with others in Chinese for daily communication\", \"score\": \"International\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u5b8c\\u5168\\u4f7f\\u2f64\\u4e2d\\u2f42\\u8fdb\\u2f8f\\u2f47\\u5e38\\u4ea4\\u6d41\", \"content_en\": \"Can communicate with others in Chinese for daily communication completely\", \"score\": \"Advanced\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 50, 33101143, '您对孩子学习中文的期望是什么？', 'What are your expectations for the child to learn Chinese?', '{\"no\": \"33101143\", \"title_zh\": \"\\u60a8\\u5bf9\\u5b69\\u5b50\\u5b66\\u4e60\\u4e2d\\u6587\\u7684\\u671f\\u671b\\u662f\\u4ec0\\u4e48\\uff1f\", \"title_en\": \"What are your expectations for the child to learn Chinese?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u4f7f\\u2f64\\u4e2d\\u2f42\\u8fdb\\u2f8f\\u2f47\\u5e38\\u4ea4\\u6d41\", \"content_en\": \"Enable to communicate with others in Chinese for daily communication\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5177\\u5907\\u81ea\\u4e3b\\u9605\\u8bfb\\u4e2d\\u6587\\u8bfb\\u7269\\u7684\\u80fd\\u529b\", \"content_en\": \"Enable to read Chinese books independently\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u63d0\\u2fbc\\u542c\\u3001\\u8bf4\\u3001\\u8bfb\\u3001\\u5199\\u6280\\u80fd\\uff0c\\u5e94\\u5bf9\\u8003\\u8bd5\", \"content_en\": \"Improve Listening, Speaking, Reading and Writing Skills\\uff0cprepare for examinations\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u63d0\\u5347\\u4e2d\\u2f42\\u2f42\\u5b66\\u7d20\\u517b\\uff08\\u5199\\u4f5c\\u3001\\u7cbe\\u8bfb\\u3001\\u4e2d\\u56fd\\u4f20\\u7edf\\u2f42\\u5316\\u5b66\\u4e60\\uff09\", \"content_en\": \"Upgrading the academic literacy (writing, intensive reading, traditional Chinese learning)\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 52, 33101033, '孩子的年级？', 'The grade of the child?', '{\"no\": \"33101033\", \"title_zh\": \"\\u5b69\\u5b50\\u7684\\u5e74\\u7ea7\\uff1f\", \"title_en\": \"The grade of the child?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u4e00\\u5e74\\u7ea7\", \"content_en\": \"Grade 1 of primary school\", \"score\": \" SG,1\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u4e8c\\u5e74\\u7ea7\", \"content_en\": \"Grade 2 of primary school\", \"score\": \" SG,2\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u4e09\\u5e74\\u7ea7\", \"content_en\": \"Grade 3 of primary school\", \"score\": \" SG,3\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u56db\\u5e74\\u7ea7\", \"content_en\": \"Grade 4 of primary school\", \"score\": \" SG,4\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u4e94\\u5e74\\u7ea7\", \"content_en\": \"Grade 5 of primary school\", \"score\": \" SG,5\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5c0f\\u5b66\\u516d\\u5e74\\u7ea7\", \"content_en\": \"Grade 6 of primary school\", \"score\": \" Advanced,3\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u4e2d\\u5b66\\u4e00\\u5e74\\u7ea7\", \"content_en\": \"Grade 1 of middle school\", \"score\": \"Advanced,4\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u4e2d\\u5b66\\u4e8c\\u5e74\\u7ea7\", \"content_en\": \"Grade 2 of middle school\", \"score\": \"Advanced,4\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u4e2d\\u5b66\\u4e09\\u5e74\\u7ea7\", \"content_en\": \"Grade 3 of middle school\", \"score\": \"Advanced,5\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u4e2d\\u5b66\\u56db\\u5e74\\u7ea7\", \"content_en\": \"Grade 4 of middle school\", \"score\": \"Advanced,5\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 53, 33101211, '您居住在哪里？', 'Where do you live?', '{\"no\": \"33101211\", \"title_zh\": \"\\u60a8\\u5c45\\u4f4f\\u5728\\u54ea\\u91cc\\uff1f\", \"title_en\": \"Where do you live?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5317\\u7f8e\\u5730\\u533a\", \"content_en\": \"North America\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u6fb3\\u5927\\u5229\\u4e9a\", \"content_en\": \"Australia\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u65b0\\u52a0\\u5761\", \"content_en\": \"Singapore\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u6b27\\u6d32\\u5730\\u533a \", \"content_en\": \"Europe\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5176\\u4ed6\\uff1a\", \"content_en\": \"Others:\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 55, 33101022, '您对孩子的中文需求是什么？', 'What are your expectations for the child to learn Chinese?', '{\"no\": \"33101022\", \"title_zh\": \"\\u60a8\\u5bf9\\u5b69\\u5b50\\u7684\\u4e2d\\u6587\\u9700\\u6c42\\u662f\\u4ec0\\u4e48\\uff1f\", \"title_en\": \"What are your expectations for the child to learn Chinese?\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u80fd\\u4f7f\\u2f64\\u4e2d\\u2f42\\u8fdb\\u2f8f\\u2f47\\u5e38\\u4ea4\\u6d41 \", \"content_en\": \"Enable to communicate with others in Chinese for daily communication\", \"score\": \"International\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u63d0\\u2fbc\\u542c\\u3001\\u8bf4\\u3001\\u8bfb\\u3001\\u5199\\u6280\\u80fd\\uff0c\\u5e94\\u5bf9\\u8003\\u8bd5\\uff08\\u5982PSLE\\uff0cSA1\\uff0cSA2\\uff09\", \"content_en\": \"Improve Listening, Speaking, Reading and Writing Skills\\uff0cprepare for examinations (e.g. PSLE, SA1, SA2)\", \"score\": \"SG\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u5168\\u2faf\\u63d0\\u5347\\u4e2d\\u2f42\\u6280\\u80fd\\u548c\\u2f42\\u5b66\\u7d20\\u517b\\uff08\\u5199\\u4f5c\\u3001\\u7cbe\\u8bfb\\u3001\\u4e2d\\u56fd\\u4f20\\u7edf\\u2f42\\u5316\\u5b66\\u4e60\\uff09\", \"content_en\": \"Upgrading the academic literacy (writing, intensive reading, traditional Chinese learning)\", \"score\": \"Advanced\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-09 12:24:11', '2020-01-09 12:24:11' ),
	( 64, 33101220, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101220\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c1\\u8bfe \\u6211\\u4e0a\\u5b66\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c2\\u8bfe \\u6211\\u5bb6\\u91cc\\u6709\\u4e5d\\u4e2a\\u4eba\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c3\\u8bfe \\u4eca\\u5929\\u662f\\u6211\\u7684\\u751f\\u65e5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c4\\u8bfe \\u6211\\u559c\\u6b22\\u6253\\u7bee\\u7403\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c5\\u8bfe \\u73b0\\u5728\\u51e0\\u70b9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c6\\u8bfe \\u6211\\u611f\\u5192\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c7\\u8bfe \\u8fd9\\u662f\\u6211\\u7684\\u5b66\\u6821\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c8\\u8bfe \\u4eca\\u5929\\u6709\\u4f53\\u80b2\\u8bfe\\u5417\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c9\\u8bfe \\u6211\\u7684\\u4e1c\\u897f\\u4e0d\\u89c1\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c10\\u8bfe \\u8bfe\\u5ba4\\u91cc\\u9762\\u6709\\u4ec0\\u4e48\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"K\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c11\\u8bfe \\u6211\\u7684\\u540c\\u5b66\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"L\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c12\\u8bfe \\u6211\\u7231\\u5e72\\u51c0\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"M\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c13\\u8bfe \\u4f60\\u770b\\u89c1\\u6211\\u7684\\u889c\\u5b50\\u4e86\\u5417\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"N\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c14\\u8bfe \\u5bb6\\u91cc\\u8fd9\\u4e48\\u5e72\\u51c0\\u554a\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"O\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c15\\u8bfe \\u4f60\\u60f3\\u5403\\u4ec0\\u4e48\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"P\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c16\\u8bfe \\u6211\\u6700\\u559c\\u6b22\\u5403\\u897f\\u74dc\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"Q\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c17\\u8bfe \\u6211\\u4eec\\u4e00\\u8d77\\u6765\\u5e86\\u795d\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"R\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c18\\u8bfe \\u5230\\u52a8\\u7269\\u56ed\\u53bb\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"S\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c19\\u8bfe \\u6211\\u5bb6\\u9644\\u8fd1\\u6709\\u516c\\u56ed\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 10:55:15', '2020-01-10 12:09:36' ),
	( 65, 33101221, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101221\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c1\\u8bfe \\u6211\\u7684\\u8863\\u670d\\u5c0f\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c2\\u8bfe \\u65b0\\u5e74\\u5230\\u6765\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c3\\u8bfe \\u5ba2\\u4eba\\u6765\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c4\\u8bfe \\u6211\\u662f\\u827a\\u672f\\u5bb6\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c5\\u8bfe \\u4eca\\u5929\\u662f\\u5b66\\u6821\\u5f00\\u653e\\u65e5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c6\\u8bfe \\u4f60\\u600e\\u4e48\\u4e0a\\u5b66\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c7\\u8bfe \\u5728\\u5496\\u5561\\u5e97\\u5403\\u65e9\\u9910\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c8\\u8bfe \\u611f\\u8c22\\u6211\\u5468\\u56f4\\u7684\\u4eba\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c9\\u8bfe \\u4eca\\u5929\\u662f\\u6674\\u5929\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c10\\u8bfe \\u5c0f\\u4fa6\\u63a2\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"K\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c11\\u8bfe \\u4f60\\u73a9\\u8fc7\\u8fd9\\u4e2a\\u6e38\\u620f\\u5417\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"L\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c12\\u8bfe \\u8fc7\\u751f\\u65e5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"M\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c13\\u8bfe \\u4f60\\u60f3\\u517b\\u4ec0\\u4e48\\u5ba0\\u7269\\t\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"N\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c14\\u8bfe \\u6211\\u548c\\u5c0f\\u4e50\\u548c\\u597d\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"O\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c15\\u8bfe \\u8fd9\\u4e9b\\u6211\\u90fd\\u7231\\u5403\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"P\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c16\\u8bfe \\u98de\\u8fdb\\u4e66\\u7684\\u4e16\\u754c\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"Q\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c17\\u8bfe \\u591c\\u5e02\\u771f\\u70ed\\u95f9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"R\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c18\\u8bfe \\u65b0\\u52a0\\u5761\\u771f\\u597d\\u73a9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"S\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c19\\u8bfe \\u6211\\u4eec\\u7684\\u751f\\u6d3b\\u5c11\\u4e0d\\u4e86\\u6c34\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 10:57:40', '2020-01-10 12:19:26' ),
	( 66, 33101222, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101222\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c1\\u8bfe \\u7f8e\\u4e3d\\u7684\\u613f\\u671b\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c2\\u8bfe \\u6211\\u7684\\u670b\\u53cb\\u548c\\u5bb6\\u4eba\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c3\\u8bfe \\u6211\\u7684\\u597d\\u4f19\\u4f34\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c4\\u8bfe \\u5947\\u5999\\u7684\\u53d8\\u5316\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c5\\u8bfe \\u96be\\u5fd8\\u7684\\u4e00\\u5929\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c6\\u8bfe \\u662f\\u6211\\u4e0d\\u597d\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c7\\u8bfe \\u7559\\u5f20\\u4fbf\\u6761\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c8\\u8bfe \\u6211\\u771f\\u80fd\\u5e72\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c9\\u8bfe \\u6211\\u6709\\u529e\\u6cd5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c10\\u8bfe \\u6211\\u4f4f\\u7684\\u5730\\u65b9\\u771f\\u5e72\\u51c0\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"K\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c11\\u8bfe \\u73af\\u4fdd\\u5c0f\\u5929\\u4f7f\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"L\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c12\\u8bfe \\u6211\\u7231\\u65b0\\u52a0\\u5761\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"M\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c13\\u8bfe \\u52a8\\u7269\\u4e16\\u754c\\t\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"N\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c14\\u8bfe \\u5947\\u5999\\u7684\\u52a8\\u7269\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"O\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c15\\u8bfe \\u534e\\u6587\\u771f\\u6709\\u8da3\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"P\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c16\\u8bfe \\u5b66\\u4e60\\u8981\\u8ba4\\u771f\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"Q\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c17\\u8bfe \\u597d\\u5b69\\u5b50\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 10:59:30', '2020-01-10 12:16:55' ),
	( 67, 33101223, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101223\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c1\\u8bfe \\u4e00\\u8d77\\u770b\\u7535\\u89c6\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c2\\u8bfe \\u6211\\u4eec\\u662f\\u5144\\u5f1f\\u59d0\\u59b9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c3\\u8bfe \\u5988\\u5988\\u5bf9\\u4e0d\\u8d77\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c4\\u8bfe \\u4eca\\u5929\\u6211\\u503c\\u65e5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c5\\u8bfe \\u6211\\u4e0d\\u6015\\u6253\\u9488\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c6\\u8bfe \\u6211\\u8981\\u53c2\\u52a0\\u4ec0\\u4e48\\u6d3b\\u52a8\\u5462\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c7\\u8bfe \\u4ed6\\u7684\\u8138\\u7ea2\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c8\\u8bfe \\u9a6c\\u8def\\u5982\\u864e\\u53e3\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c9\\u8bfe \\u7231\\u5fc3\\u65e0\\u969c\\u788d\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c10\\u8bfe \\u8fd9\\u6837\\u624d\\u5bf9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"K\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c11\\u8bfe \\u5929\\u5929\\u8fd0\\u52a8\\u8eab\\u4f53\\u597d\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"L\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c12\\u8bfe \\u6211\\u662f\\u5c0f\\u5bfc\\u6e38\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"M\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c13\\u8bfe \\u7f8e\\u7334\\u738b\\u5b59\\u609f\\u7a7a\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"N\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c14\\u8bfe \\u8fd9\\u4e2a\\u4e3b\\u610f\\u771f\\u68d2\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"O\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c15\\u8bfe \\u4e00\\u5e74\\u56db\\u5b63\\u597d\\u98ce\\u5149\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"P\", \"detail\": {\"type\": \"text\", \"content\": \"\\u7b2c16\\u8bfe \\u591a\\u5f69\\u7684\\u52a8\\u7269\\u4e16\\u754c\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 11:01:27', '2020-01-10 12:18:08' ),
	( 68, 33101224, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101224\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c1\\u8bfe/\\u9ad8\\u534e\\u7b2c1\\u8bfe   \\u5230\\u6237\\u5916\\u53bb\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c2\\u8bfe/\\u9ad8\\u534e\\u7b2c2\\u8bfe   \\u8eab\\u4f53\\u4f1a\\u8bf4\\u8bdd\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c3\\u8bfe/\\u9ad8\\u534e\\u7b2c3\\u8bfe   \\u61c2\\u4e8b\\u7684\\u4f60\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c4\\u8bfe/\\u9ad8\\u534e\\u7b2c4\\u8bfe   \\u5206\\u4eab\\u662f\\u5feb\\u4e50\\u7684\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u9ad8\\u534e\\u7b2c5\\u8bfe   \\u6211\\u95ef\\u7978\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c5\\u8bfe/\\u9ad8\\u534e\\u7b2c6\\u8bfe   \\u6211\\u7684\\u4e1c\\u897f\\u627e\\u5230\\u4e86\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c6\\u8bfe/\\u9ad8\\u534e\\u7b2c7\\u8bfe   \\u4e00\\u5343\\u6876\\u6c34\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"H\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c7\\u8bfe/\\u9ad8\\u534e\\u7b2c8\\u8bfe   \\u548c\\u65f6\\u95f4\\u8d5b\\u8dd1\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"I\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c8\\u8bfe/\\u9ad8\\u534e\\u7b2c9\\u8bfe   \\u5f88\\u4e45\\u5f88\\u4e45\\u4ee5\\u524d\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"J\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c9\\u8bfe/\\u9ad8\\u534e\\u7b2c10\\u8bfe  \\u6210\\u957f\\u7684\\u70e6\\u607c \", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"K\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c10\\u8bfe/\\u9ad8\\u534e\\u7b2c11\\u8bfe \\u540c\\u5b66\\u4e4b\\u95f4\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"L\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c11\\u8bfe/\\u9ad8\\u534e\\u7b2c12\\u8bfe \\u65b0\\u52a0\\u5761\\uff0c\\u6211\\u4e3a\\u4f60\\u9a84\\u50b2\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"M\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c12\\u8bfe/\\u9ad8\\u534e\\u7b2c13\\u8bfe \\u6c49\\u5b57\\u738b\\u56fd\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"N\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c13\\u8bfe/\\u9ad8\\u534e\\u7b2c14\\u8bfe \\u8001\\u5e08\\uff0c\\u8c22\\u8c22\\u60a8\\uff01\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"O\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c14\\u8bfe/\\u9ad8\\u534e\\u7b2c15\\u8bfe \\u60f3\\u5f53\\u4e00\\u68f5\\u6811 \", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"P\", \"detail\": {\"type\": \"text\", \"content\": \" \\u9ad8\\u534e\\u7b2c16\\u8bfe \\u8bed\\u8a00\\u7684\\u529b\\u91cf \", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"Q\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c15\\u8bfe/\\u9ad8\\u534e\\u7b2c17\\u8bfe \\u4e16\\u754c\\u90a3\\u4e48\\u5927\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 11:03:04', '2020-01-10 12:22:55' ),
	( 69, 33101225, '您的孩子目前上到了哪一课？', '', '{\"no\": \"33101225\", \"title_zh\": \"\\u60a8\\u7684\\u5b69\\u5b50\\u76ee\\u524d\\u4e0a\\u5230\\u4e86\\u54ea\\u4e00\\u8bfe\\uff1f\", \"title_en\": \"\", \"alternatives\": [{\"id\": \"A\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c1\\u8bfe/\\u9ad8\\u534e\\u7b2c1\\u8bfe   \\u52a0\\u6cb9\\u52a0\\u6cb9\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"B\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c2\\u8bfe/\\u9ad8\\u534e\\u7b2c2\\u8bfe   \\u7956\\u5b59\\u60c5\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"C\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c3\\u8bfe/\\u9ad8\\u534e\\u7b2c3\\u8bfe   \\u7f8e\\u98df\\u5c0f\\u4fa6\\u63a2\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"D\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c4\\u8bfe/\\u9ad8\\u534e\\u7b2c4\\u8bfe   \\u5b9d\\u8d35\\u7684\\u793c\\u7269\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"E\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c5\\u8bfe/\\u9ad8\\u534e\\u7b2c5\\u8bfe   \\u5c0f\\u6545\\u4e8b\\uff0c\\u5927\\u9053\\u7406\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"F\", \"detail\": {\"type\": \"text\", \"content\": \"\\u666e\\u534e\\u7b2c6\\u8bfe/\\u9ad8\\u534e\\u7b2c6\\u8bfe   \\u7cbe\\u5f69\\u4e09\\u56fd\", \"content_en\": \"\", \"score\": \"\"}}, {\"id\": \"G\", \"detail\": {\"type\": \"text\", \"content\": \"\\u9ad8\\u534e\\u7b2c7\\u8bfe   \\u4e16\\u754c\\u8d70\\u900f\\u900f\", \"content_en\": \"\", \"score\": \"\"}}]}', 1, '2020-01-10 11:04:18', '2020-01-10 11:04:18' );
            ''')
        # questions = ParentQuestionnaire.objects.filter(id__gt=max_id).all()
        #
        # for question in questions:
        #     course_question = CourseQuestionnaire()
        #     course_question.id = question.id
        #     course_question.question_no = question.no_id
        #     course_question.title_zh = question.tittle
        #     course_question.title_en = question.tittle_en
        #     detail = question.detail
        #
        #     detail = detail.replace('tittle', 'title_zh')
        #     detail = detail.replace('tittle_en', 'title_en')
        #     detail = detail.replace('title_zh_en', 'title_en')
        #
        #     course_question.detail = detail
        #     course_question.status = question.get_status_display()
        #
        #     course_question.create_time = question.created_on
        #     course_question.update_time = question.updated_on
        #     course_question.save()
        print('add_parent_question finish')

    @print_insert_table_times
    def add_class_type(self):
        try:
            with connections['lingoace'].cursor() as cursor:
                cursor.execute('''INSERT INTO `lingoacedb`.`classroom_class_type`(`id`, `name`, `user_max`, `description`, `create_time`, `update_time`) VALUES (1, 'one2one', 1, '1对1', '2019-10-09 15:21:25', NULL)''')
                cursor.execute('''INSERT INTO `lingoacedb`.`classroom_class_type`(`id`, `name`, `user_max`, `description`, `create_time`, `update_time`) VALUES (2, 'smallclass', 4, '小班课', '2019-10-09 15:21:48', NULL)''')
                cursor.execute('''INSERT INTO `lingoacedb`.`classroom_class_type`(`id`, `name`, `user_max`, `description`, `create_time`, `update_time`) VALUES (3, 'bigclass', 1000, '公开课', '2019-10-09 15:24:09', NULL)''')
        except:
            pass
        print('add_class_type finish')

    @print_insert_table_times
    def add_exchange_rate(self):

        '''货币汇率，货币单价/课时'''

        max_id = CommonExchangeRate.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        exchanges = ExchangeRate.objects.filter(id__gt=max_id).all()

        for exchange in exchanges:
            common_exchange_rate = CommonExchangeRate()
            common_exchange_rate.id = exchange.id
            common_exchange_rate.currency = exchange.currency
            currency_name = CURRENCY_CHOICES.get(exchange.currency, exchange.currency)
            common_exchange_rate.currency_en = currency_name
            common_exchange_rate.currency_zh = currency_name
            common_exchange_rate.rate = exchange.rate
            common_exchange_rate.valid_start = exchange.start_time
            common_exchange_rate.valid_end = exchange.end_time
            common_exchange_rate.recharge = CommonExchangeRate.DISPLAY
            common_exchange_rate.create_time = exchange.created_on
            common_exchange_rate.update_time = exchange.updated_on
            common_exchange_rate.save()

    @print_insert_table_times
    def add_common_coupon(self):

        max_id = CommonCoupon.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        coupons = Coupon.objects.filter(id__gt=max_id).all()
        for coupon in coupons:
            common_coupon = CommonCoupon()
            common_coupon.id = coupon.id
            common_coupon.code = coupon.code
            common_coupon.valid_start_time = coupon.valid_from
            common_coupon.valid_end_time = coupon.valid_to
            common_coupon.discount = coupon.discount
            common_coupon.status = coupon.active
            common_coupon.create_time = timezone.now()
            common_coupon.update_time = timezone.now()
            common_coupon.save()

    @print_insert_table_times
    def add_bussinessrule(self):
        max_id = CommonBussinessRule.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        business_rule_list = BusinessRule.objects.filter(id__gt=max_id).all()

        for business_rule in business_rule_list:
            common_bussiness_rule = CommonBussinessRule()
            common_bussiness_rule.id = business_rule.id
            common_bussiness_rule.course_edition_id = business_rule.programme_id
            common_bussiness_rule.class_type_id = business_rule.class_type_id
            common_bussiness_rule.rule_type = business_rule.rule_type
            common_bussiness_rule.user_level_id = business_rule.tutor_grade_id
            common_bussiness_rule.valid_start = business_rule.start_time
            common_bussiness_rule.valid_end = business_rule.end_time
            common_bussiness_rule.remark = business_rule.desc
            common_bussiness_rule.create_time = business_rule.created_on
            common_bussiness_rule.update_time = business_rule.updated_on
            common_bussiness_rule.save()

    @print_insert_table_times
    def add_ruleformula(self):

        max_id = CommonRuleFormula.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        rule_formula_list = RuleFormula.objects.filter(id__gt=max_id).all()

        for rule_formula in rule_formula_list:
            common_rule_fornula = CommonRuleFormula()
            common_rule_fornula.id = rule_formula.id
            common_rule_fornula.rule_id = rule_formula.rule_id
            common_rule_fornula.min_amount = rule_formula.min_amount
            common_rule_fornula.max_amount = rule_formula.max_amount
            common_rule_fornula.amount = rule_formula.amount
            common_rule_fornula.create_time = rule_formula.created_on
            common_rule_fornula.update_time = rule_formula.updated_on
            common_rule_fornula.save()

    @print_insert_table_times
    def add_teachplan(self, static_url):
        max_id = CourseTeacherGuidebook.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        teach_plans = TeachPlan.objects.filter(id__gt=max_id).all()
        for teach_plan in teach_plans:
            teacher_guide_book = CourseTeacherGuidebook()
            teacher_guide_book.id = teach_plan.id
            teacher_guide_book.lesson_id = teach_plan.session_id
            teacher_guide_book.tp_content = static_url + teach_plan.tp_content
            teacher_guide_book.create_time = teach_plan.created_on
            teacher_guide_book.update_time = teach_plan.updated_on
            teacher_guide_book.save()

    @print_insert_table_times
    def add_classtype_price(self):

        max_id = ClasstypePrice.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        prices = Price.objects.filter(id__gt=max_id).all()
        for price in prices:
            classtype_price = ClasstypePrice()
            classtype_price.id = price.id
            classtype_price.class_type_id = price.class_type_id
            classtype_price.course_edition_id = price.programme_id
            classtype_price.prices = price.price
            classtype_price.create_time = price.created_on
            classtype_price.update_time = price.updated_on
            classtype_price.save()

    # @print_insert_table_times
    # def add_paypal_ipn(self):
    #     max_id = NgPaypalIpn.objects.aggregate(Max('id'))
    #     max_id = max_id.get('id__max', 0)
    #     if not max_id:
    #         max_id = 0
    #     paypal_ipns = PaypalIpn.objects.filter(id__gt=max_id).all()
    #     for ipn in paypal_ipns:
    #         ng_paypal_ipn = NgPaypalIpn()
    #         ng_paypal_ipn.id = ipn.id
    #         ng_paypal_ipn.business = ipn.business
    #         ng_paypal_ipn.charset = ipn.charset
    #         ng_paypal_ipn.custom = ipn.custom
    #         ng_paypal_ipn.notify_version = ipn.notify_version
    #         ng_paypal_ipn.parent_txn_id = ipn.parent_txn_id
    #         ng_paypal_ipn.receiver_email = ipn.receiver_email
    #         ng_paypal_ipn.receiver_id = ipn.receiver_id
    #         ng_paypal_ipn.residence_country = ipn.residence_country
    #         ng_paypal_ipn.test_ipn = ipn.test_ipn
    #         ng_paypal_ipn.txn_id = ipn.txn_id
    #         ng_paypal_ipn.txn_type = ipn.txn_type
    #         ng_paypal_ipn.verify_sign = ipn.verify_sign
    #         ng_paypal_ipn.address_country = ipn.address_country
    #         ng_paypal_ipn.address_city = ipn.address_city
    #         ng_paypal_ipn.address_country_code = ipn.address_country_code
    #         ng_paypal_ipn.address_name = ipn.address_name
    #         ng_paypal_ipn.address_state = ipn.address_state
    #         ng_paypal_ipn.address_status = ipn.address_status
    #         ng_paypal_ipn.address_street = ipn.address_street
    #         ng_paypal_ipn.address_zip = ipn.address_zip
    #         ng_paypal_ipn.contact_phone = ipn.contact_phone
    #         ng_paypal_ipn.first_name = ipn.first_name
    #         ng_paypal_ipn.last_name = ipn.last_name
    #         ng_paypal_ipn.payer_business_name = ipn.payer_business_name
    #         ng_paypal_ipn.payer_email = ipn.payer_email
    #         ng_paypal_ipn.payer_id = ipn.payer_id
    #         ng_paypal_ipn.auth_amount = ipn.auth_amount
    #         ng_paypal_ipn.auth_exp = ipn.auth_exp
    #         ng_paypal_ipn.auth_id = ipn.auth_id
    #         ng_paypal_ipn.auth_status = ipn.auth_status
    #         ng_paypal_ipn.exchange_rate = ipn.exchange_rate
    #         ng_paypal_ipn.invoice = ipn.invoice
    #         ng_paypal_ipn.item_name = ipn.item_name
    #         ng_paypal_ipn.item_number = ipn.item_number
    #         ng_paypal_ipn.mc_currency = ipn.mc_currency
    #         ng_paypal_ipn.mc_fee = ipn.mc_fee
    #         ng_paypal_ipn.mc_gross = ipn.mc_gross
    #         ng_paypal_ipn.mc_handling = ipn.mc_handling
    #         ng_paypal_ipn.mc_shipping = ipn.mc_shipping
    #         ng_paypal_ipn.memo = ipn.memo
    #         ng_paypal_ipn.num_cart_items = ipn.num_cart_items
    #         ng_paypal_ipn.option_name1 = ipn.option_name1
    #         ng_paypal_ipn.option_name2 = ipn.option_name2
    #         ng_paypal_ipn.payer_status = ipn.payer_status
    #         ng_paypal_ipn.payment_date = ipn.payment_date
    #         ng_paypal_ipn.payment_gross = ipn.payment_gross
    #         ng_paypal_ipn.payment_status = ipn.payment_status
    #         ng_paypal_ipn.payment_type = ipn.payment_type
    #         ng_paypal_ipn.pending_reason = ipn.pending_reason
    #         ng_paypal_ipn.protection_eligibility = ipn.protection_eligibility
    #         ng_paypal_ipn.quantity = ipn.quantity
    #         ng_paypal_ipn.reason_code = ipn.reason_code
    #         ng_paypal_ipn.remaining_settle = ipn.remaining_settle
    #         ng_paypal_ipn.settle_amount = ipn.settle_amount
    #         ng_paypal_ipn.settle_currency = ipn.settle_currency
    #         ng_paypal_ipn.shipping = ipn.shipping
    #         ng_paypal_ipn.shipping_method = ipn.shipping_method
    #         ng_paypal_ipn.tax = ipn.tax
    #         ng_paypal_ipn.transaction_entity = ipn.transaction_entity
    #         ng_paypal_ipn.auction_buyer_id = ipn.auction_buyer_id
    #         ng_paypal_ipn.auction_closing_date = ipn.auction_closing_date
    #         ng_paypal_ipn.auction_multi_item = ipn.auction_multi_item
    #         ng_paypal_ipn.for_auction = ipn.for_auction
    #         ng_paypal_ipn.amount = ipn.amount
    #         ng_paypal_ipn.amount_per_cycle = ipn.amount_per_cycle
    #         ng_paypal_ipn.initial_payment_amount = ipn.initial_payment_amount
    #         ng_paypal_ipn.next_payment_date = ipn.next_payment_date
    #         ng_paypal_ipn.outstanding_balance = ipn.outstanding_balance
    #         ng_paypal_ipn.payment_cycle = ipn.payment_cycle
    #         ng_paypal_ipn.period_type = ipn.period_type
    #         ng_paypal_ipn.product_name = ipn.product_name
    #         ng_paypal_ipn.product_type = ipn.product_type
    #         ng_paypal_ipn.profile_status = ipn.profile_status
    #         ng_paypal_ipn.recurring_payment_id = ipn.recurring_payment_id
    #         ng_paypal_ipn.rp_invoice_id = ipn.rp_invoice_id
    #         ng_paypal_ipn.time_created = ipn.time_created
    #         ng_paypal_ipn.amount1 = ipn.amount1
    #         ng_paypal_ipn.amount2 = ipn.amount2
    #         ng_paypal_ipn.amount3 = ipn.amount3
    #         ng_paypal_ipn.mc_amount1 = ipn.mc_amount1
    #         ng_paypal_ipn.mc_amount2 = ipn.mc_amount2
    #         ng_paypal_ipn.mc_amount3 = ipn.mc_amount3
    #         ng_paypal_ipn.password = ipn.password
    #         ng_paypal_ipn.period1 = ipn.period1
    #         ng_paypal_ipn.period2 = ipn.period2
    #         ng_paypal_ipn.period3 = ipn.period3
    #         ng_paypal_ipn.reattempt = ipn.reattempt
    #         ng_paypal_ipn.recur_times = ipn.recur_times
    #         ng_paypal_ipn.recurring = ipn.recurring
    #         ng_paypal_ipn.retry_at = ipn.retry_at
    #         ng_paypal_ipn.subscr_date = ipn.subscr_date
    #         ng_paypal_ipn.subscr_effective = ipn.subscr_effective
    #         ng_paypal_ipn.subscr_id = ipn.subscr_id
    #         ng_paypal_ipn.case_creation_date = ipn.case_creation_date
    #         ng_paypal_ipn.username = ipn.username
    #         ng_paypal_ipn.case_id = ipn.case_id
    #         ng_paypal_ipn.case_type = ipn.case_type
    #         ng_paypal_ipn.receipt_id = ipn.receipt_id
    #         ng_paypal_ipn.currency_code = ipn.currency_code
    #         ng_paypal_ipn.handling_amount = ipn.handling_amount
    #         ng_paypal_ipn.transaction_subject = ipn.transaction_subject
    #         ng_paypal_ipn.ipaddress = ipn.ipaddress
    #         ng_paypal_ipn.flag = ipn.flag
    #         ng_paypal_ipn.transaction_subject = ipn.transaction_subject
    #         ng_paypal_ipn.ipaddress = ipn.ipaddress
    #         ng_paypal_ipn.flag_code = ipn.flag_code
    #         ng_paypal_ipn.flag_info = ipn.flag_info
    #         ng_paypal_ipn.query = ipn.query
    #         ng_paypal_ipn.response = ipn.response
    #         ng_paypal_ipn.created_at = ipn.created_at
    #         ng_paypal_ipn.updated_at = ipn.updated_at
    #         ng_paypal_ipn.from_view = ipn.from_view
    #         ng_paypal_ipn.mp_id = ipn.mp_id
    #         ng_paypal_ipn.option_selection1 = ipn.option_selection1
    #         ng_paypal_ipn.option_selection2 = ipn.option_selection2
    #         ng_paypal_ipn.create_time = timezone.now()
    #         ng_paypal_ipn.save()


    @print_insert_table_times
    def add_course_package(self):
        '''finance_course_package课包表  不能导'''
        return None
        CoursePackage.objects.all().delete()
        packages = Package.objects.all()

        for package in packages:
            course_package = CoursePackage()
            course_package.class_type_id = package.class_type_id
            course_package.course_edition_id = package.programme_id
            course_package.prices = package.price


    @print_insert_table_times
    def add_user_level(self):

        max_id = UserLevel.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0

        grades = Grade.objects.filter(id__gt=max_id).all()

        for grade in grades:
            user_level = UserLevel()
            user_level.id = grade.id
            user_level.role = 3
            user_level.grade = grade.grade
            user_level.remark = 'level' + str(grade.grade)
            user_level.create_time = grade.create_time
            user_level.update_time = grade.update_time
            user_level.save()

    @print_insert_table_times
    def add_virtualclass_type(self):
        try:
            with connections['lingoace'].cursor() as cursor:
                cursor.execute('''INSERT INTO `lingoacedb`.`classroom_virtualclass_type`(`id`, `name`, `create_time`, `update_time`) VALUES (1, '拓课', '2019-10-12 18:51:47', NULL)''')
                cursor.execute('''INSERT INTO `lingoacedb`.`classroom_virtualclass_type`(`id`, `name`, `create_time`, `update_time`) VALUES (2, '声网', '2019-10-12 18:52:05', NULL)''')
        except:
            pass

    @print_insert_table_times
    def add_common_ambassador_code(self):
        max_id = CommonAmbassadorCode.objects.aggregate(Max('id'))
        max_id = max_id.get('id__max', 0)
        if not max_id:
            max_id = 0
        general_codes = GeneralCode.objects.filter(id__gt=max_id).all()
        for general_code in general_codes:
            common_ambassador_code = CommonAmbassadorCode()
            common_ambassador_code.id = general_code.id
            common_ambassador_code.code = general_code.code
            common_ambassador_code.is_used = general_code.is_used
            common_ambassador_code.save()

    def handle(self, *args, **options):
        static_url = settings.MEDIA_URL
        print(static_url)
        self.add_user_level()
        self.add_course_edition()
        self.add_course_info()
        self.add_course_lesson()
        self.add_course_courseware(static_url)

        self.add_class_type()
        self.add_virtualclass_type()
        self.add_common_ambassador_code()
        self.add_homework(static_url)
        self.add_ext_course_tag()
        self.add_test_question()
        self.add_ext_course()
        self.add_ext_course_optag()
        self.add_ext_courseware(static_url)
        self.add_exchange_rate()
        self.add_common_coupon()
        self.add_bussinessrule()
        self.add_ruleformula()
        self.add_teachplan(static_url)
        self.add_classtype_price()
