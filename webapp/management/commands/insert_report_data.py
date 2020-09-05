from webapp.models import *
from django.core.management.base import BaseCommand
import re
from classroom.models import VirtualclassUnitReport, VirtualclassFirstReport, VirtualclassInfo


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--file_path',
                            dest='file_path',
                            default='')

    def handle(self, *args, **options):

        file_path = options.get('file_path', '')

        f = open(file_path, 'r', encoding='utf-8')
        pattern = re.compile('"parameter":{.*?}')
        for eachline in f:
            result = pattern.search(eachline)
            params = result.group()
            params = params[12:]
            params = json.loads(params)
            print(params)
            status = params.get('status')
            if status not in (0, 1):
                continue
            virtualclass_id = params.get('virtualClassId')
            first_report = VirtualclassFirstReport.objects.filter(virtual_class_id=virtualclass_id, status=status).first()
            if first_report:
                continue

            # start_time = params.get('startTime')
            # if start_time:
            #     start_time = datetime.datetime.utcfromtimestamp(start_time/1000)
            course_info_zh = params.get('courseInfoZh')
            course_info_en = params.get('courseInfoEh')
            core_knowledge_en = params.get('coreKnowledgeEn')
            core_knowledge_zh = params.get('coreKnowledgeZh')

            add_knowledge_en = params.get('addKnowledgeEn')
            add_knowledge_zh = params.get('addKnowledgeZh')

            classroom_feedback_en = params.get('classroomFeedbackEn')
            classroom_feedback_zh = params.get('classroomFeedbackZh')

            communication_suggestion_en = params.get('communicationSuggestionEn')
            communication_suggestion_zh = params.get('communicationSuggestionZh')

            suggest_course_info_en = params.get('suggestCourseInfoEn')
            suggest_course_info_zh = params.get('suggestCourseInfoZh')

            student_character_en = params.get('studentCharacterEn')
            student_character_zh = params.get('studentCharacterZh')

            student_background_en = params.get('studentBackgroundEn')
            student_background_zh = params.get('studentBackgroundZh')

            advisor_assistance_en = params.get('advisorAssistanceEn')
            advisor_assistance_zh = params.get('advisorAssistanceZh')

            class_type_id = params.get('classTypeId')
            tutor_user_id = params.get('tutorUserId')
            student_user_id = params.get('studentUserId')

            create_time = params.get('createTime')

            if create_time:
                create_time = datetime.datetime.utcfromtimestamp(create_time/1000)

            first_report = VirtualclassFirstReport()

            virtual_class = VirtualclassInfo.objects.filter(id=virtualclass_id).first()
            first_report.virtual_class_id = params.get('virtualClassId')
            if virtual_class:
                first_report.start_time = virtual_class.start_time

            first_report.course_info_zh = course_info_zh
            first_report.course_info_en = course_info_en


            first_report.core_knowledge_en = core_knowledge_en
            first_report.core_knowledge_zh = core_knowledge_zh

            first_report.add_knowledge_en = add_knowledge_en
            first_report.add_knowledge_zh = add_knowledge_zh

            first_report.classroom_feedback_en = classroom_feedback_en
            first_report.classroom_feedback_zh = classroom_feedback_zh

            first_report.communication_suggestion_en = communication_suggestion_en
            first_report.communication_suggestion_zh = communication_suggestion_zh

            first_report.suggest_course_info_en = suggest_course_info_en
            first_report.suggest_course_info_zh = suggest_course_info_zh

            first_report.student_character_en = student_character_en
            first_report.student_character_zh = student_character_zh

            first_report.student_background_en = student_background_en
            first_report.student_background_zh = student_background_zh

            first_report.advisor_assistance_en = advisor_assistance_en
            first_report.advisor_assistance_zh = advisor_assistance_zh

            first_report.create_time = create_time
            first_report.class_type_id = class_type_id
            first_report.student_user_id = student_user_id
            first_report.tutor_user_id = tutor_user_id

            first_report.save()



