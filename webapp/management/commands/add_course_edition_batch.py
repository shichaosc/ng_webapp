from django.core.management.base import BaseCommand
from course.models import CourseLesson, CourseUnit, CourseEdition, CourseInfo

'''配置课程'''

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--edition_name',
                            dest='edition_name',
                            default='')

        parser.add_argument('--course_name',
                            dest='course_name',
                            default='')

        parser.add_argument('--course_level',
                            dest='course_level',
                            default='')

        parser.add_argument('--course_lesson',
                            dest='course_lesson',
                            default='')

        parser.add_argument('--unit_split',
                            dest='unit_split',
                            default='')


    def handle(self, *args, **kwargs):

        edition_name = kwargs.get('edition_name')
        course_name = kwargs.get('course_name')
        course_level = int(kwargs.get('course_level'))
        course_lesson_no = int(kwargs.get('course_lesson'))
        unit_split = int(kwargs.get('unit_split'))

        course_edition = CourseEdition()
        course_edition.edition_name = edition_name

        course_edition.save()

        for level in range(1, course_level+1):

            course_info = CourseInfo()
            course_info.course_edition = course_edition
            course_info.course_level = level
            course_info.course_name = course_name
            course_info.save()

            unit_end = int(course_lesson_no//unit_split)+1
            for unit in range(1, unit_end):
                course_unit = CourseUnit()
                course_unit.course = course_info
                course_unit.unit_no = unit
                course_unit.first_lesson_no = (unit-1)*4+1
                course_unit.last_lesson_no = unit*4
                course_unit.save()

                for lesson_no in range(course_unit.first_lesson_no, course_unit.last_lesson_no+1):
                    course_lesson = CourseLesson()
                    course_lesson.unit_no = course_unit.unit_no
                    course_lesson.course = course_info
                    course_lesson.lesson_no = lesson_no
                    if lesson_no == course_unit.last_lesson_no:
                        course_lesson.unit_report = CourseLesson.REPORT
                    else:
                        course_lesson.unit_report = CourseLesson.NOT_REPORT
                    course_lesson.save()
