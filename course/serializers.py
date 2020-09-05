from rest_framework import serializers
from course.models import CourseEdition, CourseLesson, CourseInfo, CourseUnit


class CourseEditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseEdition
        fields = ('id', 'edition_name')


class CourseInfoSerializer(serializers.ModelSerializer):

    course_edition = CourseEditionSerializer()

    class Meta:
        model = CourseInfo
        fields = ('id', 'course_name', 'course_level', 'course_edition')


class CourseLessonSerializer(serializers.ModelSerializer):

    course = CourseInfoSerializer()

    class Meta:
        model = CourseLesson
        fields = ('id', 'lesson_no', 'unit_no', 'course', 'unit_lesson_no')


class CourseUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseUnit
        fields = ('id', 'unit_no', 'first_lesson_no', 'last_lesson_no')


class CourseInfoListSerializer(serializers.ModelSerializer):

    course_unit = CourseUnitSerializer(many=True)

    # child = serializers.SerializerMethodField
    # 'get_children_ordered'）
    #
    # def get_children_ordered（
    #
    #     self，parent）：
    # ＃all（）调用应该命中缓存
    # serialized_data = ChildSerializer（parent.child.all（） many = True，read_only = True，context = self.context）
    # 返回serialized_data.data

    class Meta:
        model = CourseInfo
        fields = ('id', 'course_name', 'course_level', 'course_unit')


class CourseEditionListSerializer(CourseEditionSerializer):

    course_info = CourseInfoListSerializer(many=True)

    class Meta(CourseEditionSerializer.Meta):
        fields = CourseEditionSerializer.Meta.fields + ('course_info', )


class CourseLessonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseLesson
        fields = ('id', 'lesson_no', 'unit_no', 'unit_lesson_no')
