from rest_framework import serializers
from homework.models import HomeworkQuestionInfo, HomeworkKnowledgePoint, HomeworkOutlineInfo, \
    HomeworkOutlineGroup
from django.db.models import Q
import json


class HomeworkKnowledgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeworkKnowledgePoint
        fields = ('id', 'label', 'status')


class HomeworkOutlineGroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        instance = super().create(validated_data)
        # quality = instance.quality

        # for i in range(quality):
        #     homework_question = HomeworkQuestionInfo()
        #     homework_question.lesson_id = instance.lesson_id
        #     homework_question.outline_id = instance.outline_id
        #     homework_question.outline_group_id = instance.id
        #     homework_question.type = instance.type
        #     homework_question.save()

        outline_groups = HomeworkOutlineGroup.objects.filter(sort_no__gte=instance.sort_no, lesson_id=instance.lesson_id, outline_id=instance.outline_id).filter(~Q(id=instance.id)).all()

        for outline_group in outline_groups:
            outline_group.sort_no = outline_group.sort_no + 1
            outline_group.save()
        return instance

    # def update(self, instance, validated_data):
    #
    #     instance = super().update(instance, validated_data)
    #
    #     outline_groups = HomeworkOutlineGroup.objects.filter(sort_no__lte=instance.sort_no, lesson_id=instance.lesson_id, outline_id=instance.outline_id).filter(~Q(id=instance.id)).all()
    #
    #     for outline_group in outline_groups:
    #         outline_group.sort_no = outline_group.sort_no + 1
    #         outline_group.save()
    #     return instance

    class Meta:
        model = HomeworkOutlineGroup
        fields = ('id', 'lesson', 'outline', 'type', 'name', 'remark', 'quality', 'sort_no')


class HomeworkQuestionInfoSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()  # 填空题下面的小题
    knowledge_point_remark = serializers.SerializerMethodField()
    knowledge_point_remark_content = serializers.SerializerMethodField()

    def get_knowledge_point_remark(self, obj):
        return obj.remark

    def get_knowledge_point_remark_content(self, obj):
        return obj.remark_content

    def get_children(self, obj):
        if obj.type == HomeworkQuestionInfo.READING_QUESTION:
            children_group = HomeworkOutlineGroup.objects.filter(homework_question__parent_question=obj).all().distinct()
            # children_question = HomeworkQuestionInfo.objects.filter(parent_question=obj).first()
            if children_group:
                serializer = HomeworkOutlineGroupListSerializer(children_group, many=True)
                return serializer.data

    def get_content(self, obj):
        if obj.content:
            if obj.type == HomeworkQuestionInfo.READING_QUESTION:
                return obj.content
            return eval(obj.content)

    class Meta:
        model = HomeworkQuestionInfo
        fields = ('id', 'lesson', 'outline', 'outline_group', 'parent_question_id',
                  'type', 'content', 'knowledge_point_remark', 'children', 'knowledge_point_remark_content', 'knowledge_point_id')


class HomeworkOutlineGroupListSerializer(serializers.ModelSerializer):

    homework_question = HomeworkQuestionInfoSerializer(many=True)

    class Meta:
        model = HomeworkOutlineGroup
        fields = ('id', 'outline', 'type', 'name', 'remark', 'quality', 'sort_no',
                  'homework_question')


class HomeworkOutlineInfoSerializer(serializers.ModelSerializer):

    outline_group = HomeworkOutlineGroupListSerializer(many=True)

    class Meta:
        model = HomeworkOutlineInfo
        fields = ('id', 'lesson', 'inspection_content', 'status')
