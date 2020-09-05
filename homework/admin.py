from django.contrib import admin
from homework.models import HomeworkOutlineInfo, HomeworkOutlineGroup, HomeworkQuestionInfo, HomeworkKnowledgePoint


@admin.register(HomeworkOutlineInfo)
class HomeworkOutlineInfoAdmin(admin.ModelAdmin):
    search_fields = ('lesson',)  # 指定要搜索的字段，将会出现一个搜索框让管理员搜索关键词
    list_filter = ('status', 'lesson__course__course_edition__edition_name')
    raw_id_fields = ('lesson', )

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(lesson__lesson_no=search_term)

        return queryset, use_distinct


@admin.register(HomeworkOutlineGroup)
class HomeworkOutlineGroupAdmin(admin.ModelAdmin):
    search_fields = ('lesson', )
    list_filter = ('outline__status', 'lesson__course__course_edition__edition_name')
    raw_id_fields = ('lesson', 'outline')

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(lesson__lesson_no=search_term)

        return queryset, use_distinct


@admin.register(HomeworkQuestionInfo)
class HomeworkQuestionInfoAdmin(admin.ModelAdmin):

    search_fields = ('lesson', )
    list_filter = ('outline_group__outline__status', 'lesson__course__course_edition__edition_name')
    raw_id_fields = ('lesson', 'outline', 'outline_group')

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(lesson__lesson_no=search_term)

        return queryset, use_distinct



