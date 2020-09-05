import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core import serializers
from course.forms import CoursewareForm, TeachPlanForm
from course.models import CourseInfo, CourseLesson, Courseware, \
    CourseEdition, CourseQuestionnaire, CourseAssessmentQuestion,\
    CourseHomework, CourseTeacherGuidebook
from course import utils
from tutor.models import TutorInfo
from classroom.models import ClassType
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from utils import upload_aws
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from course.serializers import CourseEditionListSerializer, CourseLessonListSerializer
from django.db.models import Q
from users.permissions import IsAuthenticated
from homework.models import HomeworkOutlineInfo, HomeworkOutlineGroup, HomeworkQuestionInfo
from utils.viewset_base import JsonResponse
from django.utils import timezone
logger = logging.getLogger('pplingo.ng_webapp.course')


@permission_required('course.can_upload_exambank')
def preview(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = None
    sessions = None
    courseware = None
    cur_course = None
    cur_session = None
    courses = CourseInfo.objects.all()

    course = request.GET.get('course')
    courseware_type = request.GET.get('courseware_type')
    if not courseware_type:
        courseware_type = 'ppt'
    if course:
        sessions = CourseLesson.objects.filter(course__id=course, status=CourseLesson.ACTIVE).order_by('lesson_no')
        cur_course = int(course)
    session = request.GET.get('session')
    if session:
        if courseware_type == 'ppt':
            courseware = Courseware.objects.filter(lesson__id=session, cw_type__in=(Courseware.PDF, Courseware.PPT)).first()
        else:
            courseware = Courseware.objects.filter(lesson__id=session,
                                                   cw_type=Courseware.COCOS).first()
        cur_session = int(session)
    cur_courseware_type = courseware_type
    courseware_types = [{'id': 'ppt', 'name': 'PPT课件'}, {'id': 'cocos', 'name': 'Cocos课件'}]
    return render(request, 'man/course/preview.html',
                  {'courses': courses, 'sessions': sessions, 'courseware': courseware,
                   'cur_course': cur_course,
                   'cur_courseware_type': cur_courseware_type,
                   'courseware_types': courseware_types,
                   'cur_session': cur_session})


@permission_required('course.can_upload_courseware')
def upload(request):
    """
    Function: upload courseware

    Description:


    Args:


    Returns:

    """
    courses = None
    coursewares = None
    form = None
    cur_course = None
    result = ''
    # Handle file upload
    if request.method == 'POST':
        result = '上传成功'
        # form = CoursewareForm(request.POST, request.FILES)
        status_type = request.POST.get('status_type', '')
        file_name = request.FILES['cw_content'].name
        file = request.FILES['cw_content']
        lesson_id = request.POST.get('lesson')
        old_lesson = CourseLesson.objects.get(id=lesson_id)
        origin_lesson_id = old_lesson.id
        cw_type = request.POST.get('cw_type', 1)

        res = upload_aws.upload_courseware(origin_lesson_id, origin_lesson_id, cw_type, file_name, file)
        if res:
            result = '上传失败'
    else:
        course_id = request.GET.get('course')
        if course_id:
            cur_course = int(course_id)
            form = CoursewareForm(course_id=course_id)
        courses = CourseInfo.objects.all()
    programmes = CourseEdition.objects.all()
    return render(request, 'man/course/upload.html',
                  {'courses': courses, 'coursewares': coursewares, 'form': form, 'programmes': programmes,
                   'result': result, 'cur_course': cur_course})


PROGRAMME_QUESTIONNAIRE = '01'  # 定版本
LEVEL_NN_QUESTIONNAIRE = '02'  # 定高级版级别
LEVEL_IN_QUESTIONNAIRE = '03'  # 定国际版级别


@login_required
def questionnaire(request):
    """
    获取不同级别的家长问卷题

    :param request:
    :return:
    """
    # PROGRAMME_QUESTIONNAIRE = '01' #定版本
    # LEVEL_NN_QUESTIONNAIRE = '02' #定高级版级别
    # LEVEL_IN_QUESTIONNAIRE = '03' #定国际版级别
    parent_questionnaire = CourseQuestionnaire.objects.values("question_no", "title_zh", "title_en", "detail").all()
    programme_list = []
    nn_list = []
    in_list = []
    for q in parent_questionnaire:
        no_id = q['question_no']
        tittle = q['title_zh']
        tittle_en = q['title_en']
        detail = q['detail']
        if PROGRAMME_QUESTIONNAIRE == utils.get_level(no_id):
            dict_tmp = ({'no_id': no_id, 'tittle': tittle, 'tittle_en': tittle_en, 'detail': detail})
            programme_list.append(dict_tmp)
        elif LEVEL_NN_QUESTIONNAIRE == utils.get_level(no_id):
            dict_tmp = ({'no_id': no_id, 'tittle': tittle, 'tittle_en': tittle_en, 'detail': detail})
            nn_list.append(dict_tmp)
        elif LEVEL_IN_QUESTIONNAIRE == utils.get_level(no_id):
            dict_tmp = ({'no_id': no_id, 'tittle': tittle, 'tittle_en': tittle_en, 'detail': detail})
            in_list.append(dict_tmp)
    json_list = [{'type': PROGRAMME_QUESTIONNAIRE, 'content': programme_list},
                 {'type': LEVEL_NN_QUESTIONNAIRE, 'content': nn_list},
                 {'type': LEVEL_IN_QUESTIONNAIRE, 'content': in_list}]
    char_list = [chr(i) for i in range(65, 91)]
    return render(request, 'man/course/questionnaire.html',
                  {'questionnaire': json.dumps(json_list), 'programme': json.dumps(PROGRAMME_QUESTIONNAIRE),
                   'nn_level': json.dumps(LEVEL_NN_QUESTIONNAIRE),
                   'in_level': json.dumps(LEVEL_IN_QUESTIONNAIRE),
                   'char_list': char_list})


@permission_required('course.can_upload_exambank')
def assessment_preview(request):
    if request.is_ajax():
        assessment_question_id = request.GET.get("assessment_question_id")
        CourseAssessmentQuestion.objects.get(pk=assessment_question_id).delete()
    courses = CourseInfo.objects.all()
    course_id = request.GET.get('course_id', None)
    if course_id:
        course = CourseInfo.objects.filter(id=course_id).first()
    else:
        course = CourseInfo.objects.all().first()
    cur_course = course.id
    assessment_question = CourseAssessmentQuestion.objects.filter(course=course)
    questions = serializers.serialize('json', assessment_question)
    return render(request, 'man/course/assessment_preview.html',
                  {'courses': courses, 'testquestions': questions, 'cur_course': cur_course})


@permission_required('course.can_upload_exambank')
def examassement_list(request):
    courses = CourseInfo.objects.all()
    assessment_question_id = request.GET.get("assessment_question_id", None)
    if assessment_question_id:
        testquestion_obj = CourseAssessmentQuestion.objects.get(pk=assessment_question_id)
        question_detail = json.loads(testquestion_obj.detail)
        return render(request, 'man/course/assessment_upload.html',
                      {'courses': courses, "testquestion_obj": testquestion_obj,
                       "question_detail": question_detail})
    return render(request, 'man/course/assessment_upload.html', {'courses': courses})


@permission_required('course.can_upload_courseware')
def homework(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = None
    lessons = None
    homeworks = None
    cur_course = None
    cur_lesson = None
    new_homework = None
    courses = CourseInfo.objects.all()
    course = request.GET.get('course')
    if course:
        lessons = CourseLesson.objects.filter(course__id=course, status=CourseLesson.ACTIVE).order_by('lesson_no')
        cur_course = int(course)
    lesson = request.GET.get('session')
    if lesson:
        new_homework = HomeworkOutlineInfo.objects.filter(lesson_id=lesson, status=HomeworkOutlineInfo.ACTIVE).first()
        homeworks = CourseHomework.objects.filter(lesson__id=lesson, status=CourseHomework.ACTIVE)
        cur_lesson = int(lesson)
    return render(request, 'man/course/homework.html',
                  {'courses': courses, 'sessions': lessons, 'homeworks': homeworks, 'cur_course': cur_course,
                   'cur_session': cur_lesson, 'new_homework': new_homework})


# @permission_required('course.can_upload_courseware')
# def homeworkupload(request):
#     """
#     Function:
#
#     Description:
#
#
#     Args:
#
#
#     Returns:
#
#     """
#     courses = None
#     homeworks = None
#     # form = None
#     lessons = None
#     cur_course = None
#     if request.method == 'POST':
#         file = request.FILES['hw_content']
#         file_name = request.FILES['hw_content'].name
#         lesson_id = request.POST.get('session')
#         CourseHomework.objects.filter(lesson__id=lesson_id).update(status=CourseHomework.ARCHIVED)
#         homework = CourseHomework()
#         hw_content = upload_aws.upload_file('hw_content', file)
#         homework.lesson = CourseLesson.objects.get(pk=lesson_id)
#         homework.hw_content = hw_content
#         homework.hw_name = file_name
#         homework.save()
#
#         homeworks = CourseHomework.objects.filter(lesson__id=lesson_id)
#     else:
#         course_id = request.GET.get('course')
#         if course_id:
#             # form = HomeworkForm(course_id=course_id)
#             cur_course = int(course_id)
#             lessons = CourseLesson.objects.filter(course_id=course_id, status=CourseLesson.ACTIVE).all()
#         courses = CourseInfo.objects.all()
#
#     return render(request, 'man/course/homeworkupload.html',
#                   {'courses': courses, 'lessons': lessons, 'homeworks': homeworks, 'cur_course': cur_course})


@permission_required('course.can_upload_courseware')
def homeworkupload(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = None
    homeworks = None
    # form = None
    lessons = None
    cur_course = None
    if request.method == 'POST':
        file = request.FILES['hw_content']
        file_name = request.FILES['hw_content'].name
        lesson_id = request.POST.get('session')
        CourseHomework.objects.filter(lesson__id=lesson_id).update(status=CourseHomework.ARCHIVED)
        homework = CourseHomework()
        hw_content = upload_aws.upload_file('hw_content', file)
        homework.lesson = CourseLesson.objects.get(pk=lesson_id)
        homework.hw_content = hw_content
        homework.hw_name = file_name
        homework.save()
        homeworks = CourseHomework.objects.filter(lesson__id=lesson_id)
        data = {'code': 0, 'message': 'success'}
        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))
    else:
        course_id = request.GET.get('course')
        if course_id:
            # form = HomeworkForm(course_id=course_id)
            cur_course = int(course_id)
            lessons = CourseLesson.objects.filter(course_id=course_id, status=CourseLesson.ACTIVE).all()
        courses = CourseInfo.objects.all()

    return render(request, 'man/course/homeworkupload.html',
                  {'courses': courses, 'lessons': lessons, 'homeworks': homeworks, 'cur_course': cur_course})


@permission_required('course.can_upload_courseware')
def teachplan(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = None
    lessons = None
    teachplans = None
    cur_course = None
    cur_lesson = None
    courses = CourseInfo.objects.all()
    course = request.GET.get('course')
    if course:
        lessons = CourseLesson.objects.filter(course__id=course, status=CourseLesson.ACTIVE).order_by('lesson_no')
        cur_course = int(course)
    lesson = request.GET.get('session')
    if lesson:
        teachplans = CourseTeacherGuidebook.objects.filter(lesson_id=lesson)
        cur_lesson = int(lesson)
    return render(request, 'man/course/teachplan.html',
                  {'courses': courses, 'sessions': lessons, 'teachplans': teachplans, 'cur_course': cur_course,
                   'cur_session': cur_lesson})


@permission_required('course.can_upload_exambank')
def teachplanupload(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = None
    teachplans = None
    form = None
    cur_course = None
    if request.method == 'POST':
        form = TeachPlanForm(request.POST, request.FILES)
        if form.is_valid():
            tp_content_file = request.FILES['tp_content']
            tp_content = upload_aws.upload_file('filer_public', tp_content_file)
            teachplan = CourseTeacherGuidebook()
            teachplan.tp_content = tp_content
            lesson_id = form.cleaned_data['session']
            exist_hw = CourseTeacherGuidebook.objects.filter(lesson_id=lesson_id)
            exist_hw.delete()

            teachplan.lesson = CourseLesson.objects.get(pk=lesson_id)
            teachplan.save()
            # teachplan.tp_content = settings.MEDIA_URL + teachplan.tp_content.name
            teachplan.save()
            teachplans = CourseTeacherGuidebook.objects.filter(lesson_id=lesson_id)
    else:
        course_id = request.GET.get('course')
        if course_id:
            form = TeachPlanForm(course_id=course_id)
            cur_course = int(course_id)
        courses = CourseInfo.objects.all()

    return render(request, 'man/course/teachplanupload.html',
                  {'courses': courses, 'form': form, 'teachplans': teachplans, 'cur_course': cur_course})


def get_courses_by_programme(request):
    courses = CourseInfo.objects.filter(course_edition=request.GET.get('programme_id'))
    data = serializers.serialize("json", courses)
    return HttpResponse(data)


@csrf_exempt
@login_required
def get_tutor_courses(request):
    tutor_name = request.GET.get('tutor_name')
    if request.method == 'POST':
        tutor_name = request.POST.get('tutor_name')
        description_zh = request.POST.get('description_zhhans')
        description_en = request.POST.get('description')
        courses_id = request.POST.get('courses_id')
        is_delete = request.POST.get('is_delete')
        class_type = request.POST.get('class_type')
        tutor = TutorInfo.objects.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)).first()
        tutor_courses = tutor.tutor_course.all()
        tutor_course_ids = [tutor_course.course.id for tutor_course in tutor_courses]
        tutor_class_types = tutor.tutor_class_type.all()
        tutor_class_type_ids = [tutor_class_type.class_type.id for tutor_class_type in tutor_class_types]
        if description_zh is not None:
            tutor.description_zh = description_zh
        if description_en is not None:
            tutor.description_en = description_en
        if courses_id is not None and is_delete is None:
            courses_id = json.loads(courses_id)
            for course in courses_id:
                if int(course) in tutor_course_ids:
                    continue
                course = CourseInfo.objects.get(id=course)
                tutor.add_course(course)
        if courses_id is not None and is_delete is not None:
            courses_id = json.loads(courses_id)

            for course in courses_id:
                if int(course) not in tutor_course_ids:
                    continue
                course = CourseInfo.objects.get(id=course)
                tutor.remove_course(course)
        if class_type is not None and is_delete is not None:
            class_type = json.loads(class_type)
            for type in class_type:
                if int(type) not in tutor_class_type_ids:
                    continue
                types = ClassType.objects.get(id=type)
                tutor.remove_classtype(types)
        if class_type is not None and is_delete is None:
            class_type = json.loads(class_type)
            for type in class_type:
                if int(type) in tutor_class_type_ids:
                    continue
                types = ClassType.objects.get(id=type)
                tutor.add_class_type(types)

        tutor.save()
        logger.debug("change tutor course, operate_user_id: {}, request_body: {}".format(request.user.id, request.body))
    data = []
    # tutors = TutorInfo.objects.filter(username=tutor_name).all()
    tutors = TutorInfo.objects.filter(Q(username=tutor_name)|Q(email=tutor_name)|Q(phone=tutor_name)).all()
    for i in tutors:
        tutor_dict = model_to_dict(i)
        tutor_dict['course'] = [course.course_id for course in i.tutor_course.all()]
        tutor_dict['class_type'] = [class_type.class_type_id for class_type in i.tutor_class_type.all()]
        tutor_dict['tutor_level'] = [tutor_level.user_level_id for tutor_level in i.tutor_level.all()]
        data.append(tutor_dict)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))


def answer_data(request, character):

    answer = 'answer{}'.format(character)
    answer_en = 'answer{}_en'.format(character)
    answer_score = 'answer{}_score'.format(character)
    answerfile = 'answerfile{}'.format(character)

    answer = request.POST.get(answer, '')
    answer_en = request.POST.get(answer_en, '')
    answer_score = request.POST.get(answer_score, '')
    answer_file = request.FILES.get(answerfile, None)
    answer_type = 'text'

    if not answer and not answer_file:
        return ''

    if answer_file:

        answer_type = utils.judge_document_type(answer_file.content_type)

        file_path = ''
        try:
            file_path = upload_aws.upload_file('exambank', answer_file)
        except Exception as e:
            logger.debug('upload file to aws fail, error={}'.format(e))
        answer = file_path

    return {'id': character,
            'detail': {
                'type': answer_type,
                'content': answer,
                'content_en': answer_en,
                'score': answer_score
            }}


@login_required
def questionnaire_upload(request):

    no_id = request.POST.get('no_id')
    title_zh = request.POST.get('tittle')
    title_en = request.POST.get('tittle_en')

    char_list = [chr(i) for i in range(65, 91)]

    alternatives = []
    for char in char_list:
        detail = answer_data(request, char)
        if detail:
            alternatives.append(detail)

    parent_questionnaire, created = CourseQuestionnaire.objects.get_or_create(question_no=no_id, status=CourseQuestionnaire.ACTIVE)
    parent_questionnaire.question_no = no_id
    parent_questionnaire.title_zh = title_zh
    parent_questionnaire.title_en = title_en

    dictjson = dict({'no': no_id, 'title_zh': title_zh, 'title_en': title_en, 'alternatives': alternatives})
    json_str = json.dumps(dictjson)
    parent_questionnaire.detail = json_str
    parent_questionnaire.save()
    return redirect('/man/course/questionnaire/')


@login_required
def questionnaire_delete(request):
    no_id = request.POST.get('no_id', '')
    CourseQuestionnaire.objects.filter(question_no=no_id).delete()
    return HttpResponse(json.dumps(no_id))


@permission_required('course.can_upload_exambank')
def exambank_preview(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    courses = CourseInfo.objects.all()

    course = request.GET.get('course')

    return render(request, 'man/course/exambank.html', {'courses': courses, 'course': course})


@permission_required('course.can_upload_exambank')
def exambank_list(request):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    msg = None
    tests = None

    # tests = CourseTest.objects.all()

    return render(request, 'man/course/exambank_upload.html', {'tests': tests})


@permission_required('course.can_upload_exambank')
def exambank_edit(request, id):
    """
    Function:

    Description:


    Args:


    Returns:

    """

    form = None
    test = None

    # test = CourseTest.objects.get(id=id)
    # form = CourseTestForm(instance=test)

    return render(request, 'man/course/exambank_upload.html', {'form': form, 'test': test})


@permission_required('course.can_upload_exambank')
def exambank_upload(request, id):
    """
    Function:

    Description:


    Args:


    Returns:

    """
    # msg = None
    #
    # instance = CourseTest.objects.filter(id=id).first()
    #
    # form = CourseTestForm(request.POST, request.FILES, instance=instance)
    #
    # if form.is_valid():
    #     form.save()
    #     messages.add_message(request, messages.SUCCESS, ('Test is uploaded successfully'))
    #
    #     return redirect('/man/exambank/list/')

    return render(request, 'man/course/exambank_upload.html')


@permission_required('course.can_upload_exambank')
def assessment_upload(request):
    courses = CourseInfo.objects.all()
    stem_no = request.POST.get('stemno')
    questiontype = request.POST.get('questiontype')
    stem_files = request.FILES.get("stem", None)
    stem_type_text = 'text'
    stem_content_text = request.POST.get('stemcontent', '')
    course_id = request.POST.get("select_value", 0)
    stem_file_type = ""
    stem_content_file = ""
    if stem_files:
        stem_file_type = utils.judge_document_type(stem_files.content_type)
        stem_content_type = stem_files.content_type
        try:
            stem_content_file = upload_aws.upload_file('exambank', stem_files)
        except Exception as e:
            logger.debug('upload stemp file fail, error={}'.format(e))

    status = request.POST.get('status')

    answerA = request.POST.get('answerA', '')
    answerfileA = request.FILES.get("answerfileA", None)
    ansewerAtype = 'text'
    if answerfileA:
        ansewerAtype = utils.judge_document_type(answerfileA.content_type)
        answerA = ''
        try:
            answerA = upload_aws.upload_file('exambank', answerfileA)
        except Exception as e:
            logger.debug('upload stem file fail, error={}'.format(e))

    answerB = request.POST.get('answerB', '')
    answerfileB = request.FILES.get("answerfileB", None)
    ansewerBtype = 'text'
    if answerfileB:
        ansewerBtype = utils.judge_document_type(answerfileB.content_type)
        answerB = ''
        try:
            answerB = upload_aws.upload_file('exambank', answerfileB)
        except Exception as e:
            logger.debug('upload stem file fail, error={}'.format(e))

    answerC = request.POST.get('answerC', '')
    answerfileC = request.FILES.get("answerfileC", None)
    ansewerCtype = 'text'
    if answerfileC:
        ansewerCtype = utils.judge_document_type(answerfileC.content_type)
        answerC = ''
        try:
            answerC = upload_aws.upload_file('exambank', answerfileC)
        except Exception as e:
            logger.debug('upload stem file fail, error={}'.format(e))

    answerD = request.POST.get('answerD', '')
    ansewerDtype = 'text'
    answerfileD = request.FILES.get("answerfileD", None)
    if answerfileD:
        ansewerDtype = utils.judge_document_type(answerfileD.content_type)
        answerD = ''
        try:
            answerD = upload_aws.upload_file('exambank', answerfileD)
        except Exception as e:
            logger.debug('upload stem file fail, error={}'.format(e))

    answercorrect = request.POST.get('answercorrect')
    difficult = request.POST.get('difficult')
    course_id = request.POST.get('course_id')
    course = CourseInfo.objects.filter(id=course_id).first()
    assessment_question, created = CourseAssessmentQuestion.objects.get_or_create(course=course, question_no=stem_no)
    assessment_question.question_type = questiontype
    assessment_question.status = status
    assessment_question.degree_of_difficulty = difficult

    alternatives = ({'id': 'A', 'detail': {'type': ansewerAtype, 'content': answerA}},
                    {'id': 'B', 'detail': {'type': ansewerBtype, 'content': answerB}},
                    {'id': 'C', 'detail': {'type': ansewerCtype, 'content': answerC}},
                    {'id': 'D', 'detail': {'type': ansewerDtype, 'content': answerD}})
    question_stem = (
        {'type': stem_type_text, 'content': stem_content_text},
        {'type': stem_file_type, 'content': stem_content_file})
    dictjson = dict({'no': stem_no, 'type': questiontype, 'stem': question_stem, 'alternatives': alternatives,
                     'answer': answercorrect, 'level': difficult})

    json_str = json.dumps(dictjson)
    assessment_question.detail = json_str
    assessment_question.save()

    return render(request, 'man/course/assessment_upload.html',
                  {'courses': courses, "CourseId": int(course_id)})


def questions(request):
    return render(request, 'man/course/homework_detail.html')


class CourseEditionViewSet(viewsets.ModelViewSet):

    serializer_class = CourseEditionListSerializer
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = CourseEdition.objects.all().prefetch_related('course_info').prefetch_related('course_info__course_unit')
        return queryset

    @action(methods=['get'], detail=True)
    def details(self, request):
        course_edition = self.get_queryset()
        course_edition_serializer = self.get_serializer(course_edition, many=True)
        return Response(course_edition_serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def lessons(self, request):
        course_id = request.query_params.get('course_id', None)
        course_lessons = CourseLesson.objects.filter(course_id=course_id, status=CourseLesson.ACTIVE).all()
        couese_lsesson_serializer = CourseLessonListSerializer(course_lessons, many=True)
        return JsonResponse(code=0, msg='success', data=couese_lsesson_serializer.data)