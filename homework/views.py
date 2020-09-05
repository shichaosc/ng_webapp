from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import filters
from utils.viewset_base import JsonResponse
from homework.models import HomeworkKnowledgePoint, HomeworkOutlineInfo, \
    HomeworkQuestionInfo, HomeworkOutlineGroup
from homework.serializer import HomeworkKnowledgeSerializer, HomeworkOutlineInfoSerializer, \
    HomeworkOutlineGroupSerializer, HomeworkQuestionInfoSerializer, HomeworkOutlineGroupListSerializer
from homework.filters import HomeworkOutlineGroupFilter
from utils import upload_aws
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response


class HomeworkKnowledgeViewSet(viewsets.ModelViewSet):

    serializer_class = HomeworkKnowledgeSerializer
    queryset = HomeworkKnowledgePoint.objects.filter(status=HomeworkKnowledgePoint.VALID).all()


class HomeworkOutlineInfoViewSet(viewsets.ModelViewSet):

    serializer_class = HomeworkOutlineInfoSerializer

    def get_queryset(self):

        queryset = HomeworkQuestionInfo.objects.filter(status__in=(HomeworkOutlineInfo.ACTIVE, HomeworkOutlineInfo.NOT_FINISH)).all()
        queryset = queryset.prefetch_related('outline_group').prefetch_related('outline_group__homework_question')
        return queryset

    @action(methods=['get'], detail=False)
    def exists(self, request):
        lesson_id = request.query_params.get('lesson_id')
        outline_info = HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.NOT_FINISH).first()
        exist = 0

        result = {
            'exist': exist,
            'outline_id': ''
        }

        if outline_info:

            outline_group = HomeworkOutlineGroup.objects.filter(outline_id=outline_info.id).first()

            if outline_group:   # 判断outline下面是否有 group 没有归档
                exist = 1
                result['exist'] = exist
                result['outline_id'] = outline_info.id
            else:
                outline_info.status = HomeworkOutlineInfo.DELETED
                outline_info.save()
                result['exist'] = exist
                result['outline_id'] = ''

        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def edit_outline(self, request):

        lesson_id = request.data.get('lesson_id')
        inspection_content = request.data.get('inspection_content')

        outline = HomeworkOutlineInfo.objects.filter(status=HomeworkOutlineInfo.NOT_FINISH, lesson_id=lesson_id).first()

        if outline:
            outline.inspection_content = inspection_content
            outline.save()
        else:
            outline = HomeworkOutlineInfo()
            outline.lesson_id = lesson_id
            outline.status = HomeworkOutlineInfo.NOT_FINISH
            outline.inspection_content = inspection_content
            outline.save()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def publish(self, request):

        lesson_id = request.data.get('lesson_id')

        outline_info = HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.NOT_FINISH).first()
        if outline_info:
            HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.ACTIVE).update(status=HomeworkOutlineInfo.ARCHIVED)
            new_outline_info = self.copy_homework_outline(outline_info)
            new_outline_info.status = HomeworkOutlineInfo.ACTIVE
            new_outline_info.save()
            return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)
        outline_info = HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.ACTIVE).first()
        if outline_info:
            return JsonResponse(code=0, msg='没有未发布的题目', status=status.HTTP_200_OK)
        return JsonResponse(code=1, msg='未查询到可用题目', status=status.HTTP_200_OK)

    def copy_homework_outline(self, outline_info):
        new_outline_info = HomeworkOutlineInfo()
        new_outline_info.lesson_id = outline_info.lesson_id
        new_outline_info.inspection_content = outline_info.inspection_content
        new_outline_info.status = HomeworkOutlineInfo.NOT_FINISH
        new_outline_info.save()
        outline_groups = HomeworkOutlineGroup.objects.filter(outline_id=outline_info.id, homework_question__parent_question_id__isnull=True).all().distinct()
        for group in outline_groups:
            new_outline_group = HomeworkOutlineGroup()
            new_outline_group.lesson_id = group.lesson_id
            new_outline_group.outline_id = new_outline_info.id
            new_outline_group.type = group.type
            new_outline_group.name = group.name
            new_outline_group.remark = group.remark
            new_outline_group.quality = group.quality
            new_outline_group.sort_no = group.sort_no
            new_outline_group.save()
            questions = HomeworkQuestionInfo.objects.filter(outline_group_id=group.id, parent_question_id__isnull=True).all()
            for question in questions:
                new_question = HomeworkQuestionInfo()
                new_question.lesson_id = question.lesson_id
                new_question.outline_id = new_outline_info.id
                new_question.outline_group_id = new_outline_group.id
                new_question.parent_question_id = question.parent_question_id
                new_question.type = question.type
                new_question.content = question.content
                new_question.knowledge_point_id = question.knowledge_point_id
                new_question.remark = question.remark
                new_question.remark_content = question.remark_content
                new_question.save()
                if group.type == HomeworkOutlineGroup.READING_QUESTION:
                    self.add_children_question(question, new_question, new_outline_info)
        return new_outline_info

    def add_children_question(self, parent_question, new_parent_question, new_outline):
        outline_groups = HomeworkOutlineGroup.objects.filter(homework_question__parent_question_id=parent_question.id).all().distinct()
        for group in outline_groups:
            new_outline_group = HomeworkOutlineGroup()
            new_outline_group.lesson_id = group.lesson_id
            new_outline_group.outline_id = new_outline.id
            new_outline_group.type = group.type
            new_outline_group.name = group.name
            new_outline_group.remark = group.remark
            new_outline_group.quality = group.quality
            new_outline_group.sort_no = group.sort_no
            new_outline_group.save()
            questions = HomeworkQuestionInfo.objects.filter(outline_group_id=group.id, parent_question_id=parent_question.id).all()
            for question in questions:
                new_question = HomeworkQuestionInfo()
                new_question.lesson_id = question.lesson_id
                new_question.outline_id = new_outline.id
                new_question.outline_group_id = new_outline_group.id
                new_question.parent_question_id = new_parent_question.id
                new_question.type = question.type
                new_question.content = question.content
                new_question.knowledge_point_id = question.knowledge_point_id
                new_question.remark = question.remark
                new_question.remark_content = question.remark_content
                new_question.save()


class HomeworkOutlineGroupViewSet(viewsets.ModelViewSet):

    serializer_class = HomeworkOutlineGroupSerializer
    queryset = HomeworkOutlineGroup.objects.filter(homework_question__parent_question__isnull=True, outline__status=HomeworkOutlineInfo.NOT_FINISH).all().distinct()
    filter_class = HomeworkOutlineGroupFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    order_fields = ('sort_no', )

    def get_serializer_class(self):
        if self.action == 'list':
            return HomeworkOutlineGroupListSerializer
        else:
            return HomeworkOutlineGroupSerializer

    @action(methods=['put'], detail=True)
    def change_sort(self, request, pk):
        outline_group = self.get_object()
        sort_no = int(request.data.get('sort_no'))
        if sort_no < outline_group.sort_no:
            outline_groups = HomeworkOutlineGroup.objects.filter(lesson_id=outline_group.lesson_id, outline_id=outline_group.outline_id, sort_no__lt=outline_group.sort_no, sort_no__gte=sort_no).all()
            for group in outline_groups:
                group.sort_no = group.sort_no + 1
                group.save()
        else:
            outline_groups = HomeworkOutlineGroup.objects.filter(lesson_id=outline_group.lesson_id, outline_id=outline_group.outline_id, sort_no__lte=sort_no, sort_no__gt=outline_group.sort_no).all()

            for group in outline_groups:
                group.sort_no = group.sort_no - 1
                group.save()
        outline_group.sort_no = sort_no
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def add_outlines(self, request):
        lesson_id = request.data.get('lesson_id')
        types = request.data.get('types', [])
        qualitys = request.data.get('qualitys', [])

        types_length = len(types)
        sort_no = 1
        outline_info = HomeworkOutlineInfo()
        outline_info.lesson_id = lesson_id
        outline_info.status = HomeworkOutlineInfo.NOT_FINISH
        outline_info.inspection_content = ''
        HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.NOT_FINISH).update(status=HomeworkOutlineInfo.DELETED)
        outline_info.save()

        for i in range(types_length):
            outline_group = HomeworkOutlineGroup()
            outline_group.type = types[i]
            outline_group.quality = qualitys[i]
            outline_group.lesson_id = lesson_id
            outline_group.outline_id = outline_info.id
            outline_group.sort_no = sort_no
            outline_group.save()

            sort_no = sort_no + 1

        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def update_outlines(self, request):
        outline_group_ids = request.data.get('outline_group_ids')
        del_outline_group_ids = request.data.get('del_outline_group_ids', [])
        types = request.data.get('types')
        qualitys = request.data.get('qualitys')
        lesson_id = request.data.get('lesson_id')
        outline_info = HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.NOT_FINISH).first()
        length = len(outline_group_ids)

        for i in range(length):
            if outline_group_ids[i] == 'add':
                outline_group = HomeworkOutlineGroup()
                outline_group.sort_no = i + 1
                outline_group.quality = qualitys[i]
                outline_group.type = types[i]
                outline_group.lesson_id = lesson_id
                outline_group.outline_id = outline_info.id
                outline_group.save()
            else:
                instance = HomeworkOutlineGroup.objects.filter(id=outline_group_ids[i]).first()
                instance.sort_no = i + 1
                instance.quality = qualitys[i]
                instance.save()
        HomeworkOutlineGroup.objects.filter(id__in=del_outline_group_ids).delete()
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        instance = HomeworkOutlineGroup.objects.get(id=id)

        if instance.type == HomeworkOutlineGroup.READING_QUESTION:
            questions = HomeworkQuestionInfo.objects.filter(outline_group_id=id, type=HomeworkQuestionInfo.READING_QUESTION).all().only('id')

            question_ids = [question.id for question in questions]
            children_questions = HomeworkQuestionInfo.objects.filter(parent_question_id__in=question_ids).all().only('outline_group_id')
            outline_group_id_list = [children_question.outline_group_id for children_question in children_questions]
            HomeworkOutlineGroup.objects.filter(id__in=outline_group_id_list).delete()
        instance.delete()
        outline_groups = HomeworkOutlineGroup.objects.filter(sort_no__gt=instance.sort_no, lesson_id=instance.lesson_id, outline_id=instance.outline_id).all()

        for outline_group in outline_groups:
            outline_group.sort_no = outline_group.sort_no - 1
            outline_group.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class HomeworkQuestionViewSet(viewsets.ModelViewSet):

    serializer_class = HomeworkQuestionInfoSerializer
    queryset = HomeworkQuestionInfo.objects.all()

    @action(methods=['post'], detail=False)
    def add_questions(self, request):
        outline_id = request.data.get('outline_id')
        lesson_id = request.data.get('lesson_id')
        outline_status = int(request.data.get('status'))
        outline_groups = request.data.get('outline_group')

        for group in outline_groups:
            outline_group_id = group['outline_group_id']
            outline_group = HomeworkOutlineGroup.objects.get(id=outline_group_id)
            homeworks = group['homework']
            quality = len(homeworks)
            outline_group.quality = quality
            outline_group.save()
            if outline_status == HomeworkOutlineInfo.ACTIVE:  # 发布这套题，删除没有题的大纲
                if not homeworks:
                    outline_group.delete()
                    continue

            for homework in homeworks:
                id = homework.pop('id', None)
                if id:   # 有id就更新
                    question = HomeworkQuestionInfo.objects.get(id=id)
                else:
                    question = HomeworkQuestionInfo()

                knowledge_point_id = homework.pop('knowledge_point_id', None)
                knowledge_point_remark = homework.pop('knowledge_point_remark', None)
                knowledge_point_remark_content = homework.pop('knowledge_point_remark_content', None)
                question.outline_id = outline_id
                question.outline_group_id = outline_group_id
                question.lesson_id = lesson_id
                question.type = outline_group.type
                question.remark = knowledge_point_remark
                question.remark_content = knowledge_point_remark_content
                question.knowledge_point_id = knowledge_point_id

                if outline_group.type == HomeworkOutlineGroup.READING_QUESTION:
                    '''填空题， 下面的题重新生成outline_group'''
                    htmlArticle = homework.pop('htmlArticle', '')
                    question.content = htmlArticle
                    question.save()

                    childrens = homework['children']
                    for children in childrens:
                        children_outline_group_id = children.pop('outline_group_id', None)
                        if children_outline_group_id:
                            children_outline_group = HomeworkOutlineGroup.objects.get(id=children_outline_group_id)
                        else:
                            children_outline_group = HomeworkOutlineGroup()
                        children_outline_group_name = children.pop('outline_group_name', None)
                        children_outline_group_remark = children.pop('outline_group_remark', None)

                        outline_group_type = children.pop('type', None)
                        children_outline_group.lesson_id = lesson_id
                        children_outline_group.outline_id = outline_id
                        children_outline_group.type = outline_group_type
                        children_outline_group.sort_no = 1
                        children_outline_group.name = children_outline_group_name
                        children_outline_group.remark = children_outline_group_remark
                        children_questions = children.pop('children_question', [])
                        children_outline_group.quality = len(children_questions)
                        children_outline_group.save()
                        for children_question in children_questions:
                            children_question_id = children_question.pop('question_id', None)
                            if children_question_id:
                                children_question_instance = HomeworkQuestionInfo.objects.get(id=children_question_id)
                            else:
                                children_question_instance = HomeworkQuestionInfo()
                            children_knowledge_point_id = children_question.pop('knowledge_point_id', None)
                            children_knowledge_point_remark = children_question.pop('knowledge_point_remark', None)
                            children_knowledge_point_remark_content = children_question.pop('knowledge_point_remark_content', None)
                            children_question_instance.outline_id = outline_id
                            children_question_instance.outline_group_id = children_outline_group.id
                            children_question_instance.lesson_id = lesson_id
                            children_question_instance.type = children_outline_group.type
                            children_question_instance.remark = children_knowledge_point_remark
                            children_question_instance.knowledge_point_id = children_knowledge_point_id
                            children_question_instance.parent_question = question
                            children_question_instance.content = children_question
                            children_question_instance.remark_content = children_knowledge_point_remark_content
                            children_question_instance.save()
                    continue
                elif outline_group.type == HomeworkOutlineGroup.MULTIPLE_CHOICE_QUESTION:
                    options = homework['options']
                    homework["answer"] = options[0]
                    question.content = homework
                    question.save()
                    continue
                else:
                    question.content = homework
                    question.save()
        if outline_status == HomeworkOutlineInfo.ACTIVE:
            HomeworkOutlineInfo.objects.filter(lesson_id=lesson_id, status=HomeworkOutlineInfo.ACTIVE).update(
                status=HomeworkOutlineInfo.ARCHIVED)
        outline = HomeworkOutlineInfo.objects.get(id=outline_id)
        outline.status = outline_status
        outline.save()
        if outline_status == HomeworkOutlineInfo.ACTIVE:
            self.copy_homework_outline(outline)
        return JsonResponse(code=0, msg='success', status=status.HTTP_200_OK)

    def copy_homework_outline(self, outline_info):
        new_outline_info = HomeworkOutlineInfo()
        new_outline_info.lesson_id = outline_info.lesson_id
        new_outline_info.inspection_content = outline_info.inspection_content
        new_outline_info.status = HomeworkOutlineInfo.NOT_FINISH
        new_outline_info.save()
        outline_groups = HomeworkOutlineGroup.objects.filter(outline_id=outline_info.id, homework_question__parent_question_id__isnull=True).all().distinct()
        for group in outline_groups:
            new_outline_group = HomeworkOutlineGroup()
            new_outline_group.lesson_id = group.lesson_id
            new_outline_group.outline_id = new_outline_info.id
            new_outline_group.type = group.type
            new_outline_group.name = group.name
            new_outline_group.remark = group.remark
            new_outline_group.quality = group.quality
            new_outline_group.sort_no = group.sort_no
            new_outline_group.save()
            questions = HomeworkQuestionInfo.objects.filter(outline_group_id=group.id, parent_question_id__isnull=True).all()
            for question in questions:
                new_question = HomeworkQuestionInfo()
                new_question.lesson_id = question.lesson_id
                new_question.outline_id = new_outline_info.id
                new_question.outline_group_id = new_outline_group.id
                new_question.parent_question_id = question.parent_question_id
                new_question.content = question.content
                new_question.type = question.type
                new_question.knowledge_point_id = question.knowledge_point_id
                new_question.remark = question.remark
                new_question.remark_content = question.remark_content
                new_question.save()
                if group.type == HomeworkOutlineGroup.READING_QUESTION:
                    self.add_children_question(question, new_question, new_outline_info)
        return new_outline_info

    def add_children_question(self, parent_question, new_parent_question, new_outline):
        outline_groups = HomeworkOutlineGroup.objects.filter(homework_question__parent_question_id=parent_question.id).all().distinct()
        for group in outline_groups:
            new_outline_group = HomeworkOutlineGroup()
            new_outline_group.lesson_id = group.lesson_id
            new_outline_group.outline_id = new_outline.id
            new_outline_group.type = group.type
            new_outline_group.name = group.name
            new_outline_group.remark = group.remark
            new_outline_group.quality = group.quality
            new_outline_group.sort_no = group.sort_no
            new_outline_group.save()
            questions = HomeworkQuestionInfo.objects.filter(outline_group_id=group.id, parent_question_id=parent_question.id).all()
            for question in questions:
                new_question = HomeworkQuestionInfo()
                new_question.lesson_id = question.lesson_id
                new_question.outline_id = new_outline.id
                new_question.outline_group_id = new_outline_group.id
                new_question.parent_question_id = new_parent_question.id
                new_question.type = question.type
                new_question.content = question.content
                new_question.knowledge_point_id = question.knowledge_point_id
                new_question.remark = question.remark
                new_question.remark_content = question.remark_content
                new_question.save()

    @action(methods=['post'], detail=False)
    def upload_question_img(self, request):

        file = request.data.get('image_file')
        result = upload_aws.upload_file('hw_content', file)

        return JsonResponse(code=0, msg='success', data=result, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.parent_user_id:
        #     questions = HomeworkQuestionInfo.objects.filter(outline_group_id=instance.outline_group_id).all()
        #     if len(questions) == 1:
        #         for question in questions:
        #             HomeworkOutlineGroup.objects.filter(id=question.outline_group_id).delete()
        if instance.quality == HomeworkQuestionInfo.READING_QUESTION:
            questions = HomeworkQuestionInfo.objects.filter(parent_question_id=instance.id).all()
            for question in questions:
                if question.outline_group_id:
                    HomeworkOutlineGroup.objects.filter(id=question.outline_group_id).delete()
        super(HomeworkQuestionViewSet, self).destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        HomeworkQuestionInfo.objects.filter(id=instance.id).delete()