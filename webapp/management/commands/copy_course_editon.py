from django.core.management.base import BaseCommand
from course.models import CourseLesson, CourseUnit, CourseEdition, CourseInfo

'''新增的课程信息跟旧的一样'''

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--edition_name',
                            dest='edition_name',
                            default='')

        parser.add_argument('--new_edition_name',
                            dest='new_edition_name',
                            default='')

    def handle(self, *args, **kwargs):

        edition_name = kwargs.get('edition_name')
        new_edition_name = kwargs.get('new_edition_name')

        course_edition = CourseEdition.objects.filter(edition_name=edition_name).first()
        '''新增course_edition'''
        new_course_edition = CourseEdition.objects.filter(edition_name=new_edition_name).first()
        # new_course_edition = CourseEdition()
        # new_course_edition.edition_name = new_edition_name
        # new_course_edition.description = new_edition_name
        # new_course_edition.save()
        if not new_course_edition:
            # new_course_edition.delete()
            new_course_edition = CourseEdition()
            new_course_edition.edition_name = new_edition_name
            new_course_edition.description = new_edition_name
            new_course_edition.save()
        course_infos = CourseInfo.objects.filter(course_edition_id=course_edition.id).all()

        for course_info in course_infos:
            '''新增course_info'''
            new_course_info = CourseInfo()
            new_course_info.course_edition_id = new_course_edition.id
            new_course_info.course_level = course_info.course_level
            new_course_info.course_name = new_course_edition.edition_name + ' L' + str(course_info.course_level)
            new_course_info.save()

            course_units = CourseUnit.objects.filter(course_id=course_info.id)

            for course_unit in course_units:
                '''新增course_unit'''
                new_course_unit = CourseUnit()
                new_course_unit.course_id = new_course_info.id
                new_course_unit.unit_no = course_unit.unit_no
                new_course_unit.first_lesson_no = course_unit.first_lesson_no
                new_course_unit.last_lesson_no = course_unit.last_lesson_no
                new_course_unit.save()

            course_lessons = CourseLesson.objects.filter(course_id=course_info.id, status=CourseLesson.ACTIVE).all()

            for course_lesson in course_lessons:
                '''新增course_lesson'''
                new_course_lesson = CourseLesson()
                new_course_lesson.course_id = new_course_info.id
                new_course_lesson.unit_no = course_lesson.unit_no
                new_course_lesson.unit_report = course_lesson.unit_report
                new_course_lesson.lesson_no = course_lesson.lesson_no
                new_course_lesson.unit_lesson_no = course_lesson.unit_lesson_no
                new_course_lesson.status = course_lesson.status
                new_course_lesson.save()




