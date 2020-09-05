from django.contrib import admin
from course.models import CourseAssessmentQuestion, CourseAssessmentResult, Courseware, \
    CourseEdition, CourseExtcourse, CourseExtcourseOptag, CourseExtcourseOwner, CourseExtcourseTag, \
    CourseExtcourseware, CourseHomework, CourseInfo, \
    CourseLesson, CourseQuestionnaire, CourseQuestionnaireResult, CourseUnit


class CourseAssessmentResultAdmin(admin.ModelAdmin):

    search_fields = ('student_user__real_name', )


class CoursewareAdmin(admin.ModelAdmin):

    search_fields = ('lesson__lesson_no', )
    list_filter = ('cw_type', 'lesson__status')


class CourseExtcourseAdmin(admin.ModelAdmin):

    search_fields = ('id', )
    list_filter = ('ext_course_type', 'ext_course_status', 'ext_course_active')


class CourseHomeworkAdmin(admin.ModelAdmin):

    list_filter = ('status', )
    search_fields = ('lesson__id',)


class CourseQuestionnaireAdmin(admin.ModelAdmin):
    list_filter = ('status', )


class CourseLessonAdmin(admin.ModelAdmin):

    search_fields = ('lesson_no', )
    list_filter = ('status',)

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(lesson_no=search_term)

        return queryset, use_distinct


@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):

    search_fields = ('unit_no',)
    raw_id_fields = ('course', )


admin.site.register(CourseAssessmentResult, CourseAssessmentResultAdmin)
admin.site.register(Courseware, CoursewareAdmin)
admin.site.register(CourseEdition)
admin.site.register(CourseExtcourse, CourseExtcourseAdmin)
admin.site.register(CourseExtcourseOptag)
admin.site.register(CourseExtcourseOwner)
admin.site.register(CourseExtcourseTag)
admin.site.register(CourseExtcourseware)
admin.site.register(CourseHomework, CourseHomeworkAdmin)
admin.site.register(CourseInfo)
admin.site.register(CourseLesson, CourseLessonAdmin)
admin.site.register(CourseQuestionnaire, CourseQuestionnaireAdmin)
admin.site.register(CourseAssessmentQuestion)
admin.site.register(CourseQuestionnaireResult)
