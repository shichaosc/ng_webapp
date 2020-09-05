from django.core.management.base import BaseCommand
from tutor.models import TutorInfo
from scheduler.models import ScheduleTutorClasstype, ScheduleTutorCourse, ScheduleTutorLevel
from course.models import CourseInfo, CourseEdition

'''高级版国际版小班课课程上线以后需要配置老师
   可以教高级版国际版的小班课的老师也可以教国际版高级版小班课，能教的level是3
'''

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--course_edition_name',
                            dest='course_edition_name',
                            default='')

    def handle(self, *args, **kwargs):

        advance_group_tutors = TutorInfo.objects.filter(tutor_class_type__class_type_id=2, tutor_course__course__course_edition_id=1).all().distinct()
        print(advance_group_tutors.query)
        advance_group_edition = CourseEdition.objects.filter(edition_name='Advanced Group').first()

        if not advance_group_edition:
            print("not found Advanced Group")
            return

        for tutor in advance_group_tutors:
            advance_tutor_courses = ScheduleTutorCourse.objects.filter(tutor_user_id=tutor.id, course__course_edition_id=1).select_related('course').all().distinct()
            print(advance_tutor_courses.query)
            if len(advance_tutor_courses) > 0:
                tutor_level = ScheduleTutorLevel()
                tutor_level.tutor_user_id = tutor.id
                tutor_level.course_edition_id = advance_group_edition.id
                tutor_level.user_level_id = 3
                tutor_level.save()
            for advance_tutor_course in advance_tutor_courses:
                targe_course = CourseInfo.objects.filter(course_level=advance_tutor_course.course.course_level, course_edition_id=advance_group_edition.id).first()
                if not targe_course:
                    continue
                tutor_course = ScheduleTutorCourse.objects.filter(tutor_user_id=tutor.id, course_id=targe_course.id).first()
                if tutor_course:
                    continue
                tutor_course = ScheduleTutorCourse()
                tutor_course.tutor_user_id = tutor.id
                tutor_course.course_id = targe_course.id
                tutor_course.save()

        international_group_tutors = TutorInfo.objects.filter(tutor_class_type__class_type_id=2, tutor_course__course__course_edition_id=2).all()
        print(international_group_tutors.query)
        international_group_edition = CourseEdition.objects.filter(edition_name='International Group').first()
        if not international_group_edition:
            print("not found International Group")
            return
        for tutor in international_group_tutors:
            international_tutor_courses = ScheduleTutorCourse.objects.filter(tutor_user_id=tutor.id, course__course_edition_id=2).all().distinct()
            print(international_tutor_courses.query)
            if len(international_tutor_courses) > 0:
                tutor_level = ScheduleTutorLevel()
                tutor_level.tutor_user_id = tutor.id
                tutor_level.course_edition_id = international_group_edition.id
                tutor_level.user_level_id = 3
                tutor_level.save()
            for international_tutor_course in international_tutor_courses:
                target_course = CourseInfo.objects.filter(course_level=international_tutor_course.course.course_level, course_edition_id=international_group_edition.id).first()
                if not target_course:
                    continue
                tutor_course = ScheduleTutorCourse.objects.filter(tutor_user_id=tutor.id, course_id=target_course.id).first()
                if tutor_course:
                    continue
                tutor_course = ScheduleTutorCourse()
                tutor_course.tutor_user_id = tutor.id
                tutor_course.course_id = target_course.id
                tutor_course.save()



