import os, re

from django.conf import settings
from django.core.cache import cache

from docx import Document

from course.models import CourseLesson, CourseInfo


def get_level(questionnaire_no):
    questionnaire_no = str(questionnaire_no)
    level = questionnaire_no[3:5]

    return level


def upload_audio(audio_file, audio_path):
    with open(audio_path, "wb") as f:
        for i in audio_file.chunks():
            f.write(i)

    return "ok"


def get_question_list(path):
    questions = get_all_question_list(path)

    questions = [x for x in questions if x['status']]

    return questions


def get_all_question_list(path):
    questions = cache.get(path)

    # return cached all questions
    if questions:
        return questions

    doc = Document(os.path.join(settings.MEDIA_ROOT, path))

    questions = []

    part = None
    question = None

    part_dict = {'no': '编号', 'stem': '题目', 'alternative': '选项', 'answer': '正确答案', 'level': '难度系数', 'status': '状态'}
    for para in doc.paragraphs:

        m = re.search(r"\[(.*?)\]", para.text)
        if m:
            part = m.group(1)
            # print(part)

            p = para.text
            p = p.replace(m.group(0), '', 1)
            # print(p)

            if part == part_dict['no']:
                question = {}
                question['no'] = p
                questions.append(question)
            elif part == part_dict['stem']:
                question['stem'] = []
                question['stem'].append(p)

                question['alternative'] = {}
                question['status'] = True

            elif part == part_dict['alternative']:
                alter = p.split(':', 1)
                question['alternative'].update({alter[0]: alter[1]})
                # print(alter[0])
                # print(alter[1])
            elif part == part_dict['answer']:
                question['answer'] = p
            elif part == part_dict['level']:
                question['level'] = p
            elif part == part_dict['status']:
                if p == 'F':
                    question['status'] = False
        else:
            if part == part_dict['stem']:
                p = para.text
                question['stem'].append(p)
                # print(p)

    cache.set(path, questions, 24 * 60 * 60)

    return questions


def get_next_lesson(lesson):
    try:
        next_lesson = CourseLesson.objects.get(course=lesson.course, lesson_no=lesson.lesson_no + 1, status=CourseLesson.ACTIVE)
    except CourseLesson.DoesNotExist:
        try:
            course = CourseInfo.objects.get(course_edition=lesson.course.course_edition,
                                        course_level=lesson.course.course_level + 1)
            next_lesson = CourseLesson.objects.filter(course=course, lesson_no=1, status=CourseLesson.ACTIVE).first()
        except CourseInfo.DoesNotExist:
            return None
        except CourseLesson.DoesNotExist:
            return None
    return next_lesson


def judge_document_type(content_type):
    '''
    判断文件类型
    :return:
    '''
    if content_type == 'image/jpeg':
        return 'image'
    return 'audio'
