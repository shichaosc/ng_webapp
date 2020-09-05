from webapp.models import *
from django.core.management.base import BaseCommand
import re
from classroom.models import VirtualclassUnitReport


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--file_path',
                            dest='file_path',
                            default='')

    def handle(self, *args, **options):

        file_path = options.get('file_path', '')

        f = open(file_path, 'r', encoding='utf-8')
        pattern = re.compile('"parameter":{.*?},"description"')
        # start_time_pattern = re.compile('"startTime":.*?,')
        for eachline in f:
            result = pattern.search(eachline)
            # start_time_result = start_time_pattern.search(eachline)
            # start_time = start_time_result.group()
            # start_time = start_time[12:]
            # start_time = start_time[:-1]
            if not result:
                continue
            params = result.group()
            params = params[12:]
            params = params[:-14]
            params = json.loads(params)
            status = params.get('status')
            if status not in (0, 1):
                continue
            virtualclass_id = params.get('virtualClassId')
            unit_report = VirtualclassUnitReport.objects.filter(virtual_class_id=virtualclass_id, status=status).first()
            if unit_report:
                continue
            #
            # if start_time:
            #     start_time = datetime.datetime.utcfromtimestamp(int(start_time)/1000)
            create_time = params.get('createTime')
            if create_time:
                create_time = datetime.datetime.utcfromtimestamp(create_time/1000)

            class_type_id = params.get('classTypeId')
            class_id = params.get('classId')
            first_lesson_no = params.get('firstLessonNo')
            last_lesson_no = params.get('lastLessonNo')
            unit_no = params.get('unitNo')
            first_start_time = params.get('firstStartTime')
            if first_start_time:
                first_start_time = datetime.datetime.utcfromtimestamp(first_start_time/1000)
            last_start_time = params.get('lastStartTime')
            if last_start_time:
                last_start_time = datetime.datetime.utcfromtimestamp(last_start_time/1000)

            tutor_user_id = params.get('tutorUserId')
            student_user_id = params.get('studentUserId')
            skill_assessment_en = params.get('skillAssessmentEn')
            skill_assessment_zh = params.get('skillAssessmentZh')

            classroom_performance_en = params.get('classroomPerformanceEn')
            classroom_performance_zh = params.get('classroomPerformanceZh')

            improvement_point_en = params.get('improvementPointEn')
            improvement_point_zh = params.get('improvementPointZh')

            learning_suggestion_en = params.get('learningSuggestionEn')
            learning_suggestion_zh = params.get('learningSuggestionZh')

            remark = params.get('remark')

            unit_report = VirtualclassUnitReport()

            unit_report.virtual_class_id = virtualclass_id
            unit_report.status = status
            unit_report.class_type_id = class_type_id
            unit_report.first_lesson_no = first_lesson_no
            unit_report.last_lesson_no = last_lesson_no
            unit_report.unit_no = unit_no
            unit_report.first_start_time = first_start_time
            unit_report.last_start_time = last_start_time
            unit_report.tutor_user_id = tutor_user_id
            unit_report.student_user_id = student_user_id
            unit_report.skill_assessment_en = skill_assessment_en
            unit_report.skill_assessment_zh = skill_assessment_zh

            unit_report.classroom_performance_en = classroom_performance_en
            unit_report.classroom_performance_zh = classroom_performance_zh

            unit_report.improvement_point_en = improvement_point_en
            unit_report.improvement_point_zh = improvement_point_zh

            unit_report.learning_suggestion_en = learning_suggestion_en
            unit_report.learning_suggestion_zh = learning_suggestion_zh

            unit_report.remark = remark
            unit_report.create_time = create_time
            unit_report.class_field_id = class_id
            unit_report.save()



