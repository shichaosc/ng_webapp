from django.contrib import admin
from scheduler.models import StudentTimetable, ScheduleVirtualclassMember, \
    ScheduleTutorClasstype, ScheduleTutorCourse, ScheduleTutorLevel, TutorTimetable
from tutor.models import TutorInfo
from student.models import UserStudentInfo


class StudentTimetableAdmin(admin.ModelAdmin):

    list_display = ('id', 'tutor_user_name', 'student_user_name', 'start_time', 'virtual_class_id', 'status')
    search_fields = ('id', )
    raw_id_fields = ('tutor_user', 'class_field', 'virtual_class', 'student_user')
    list_filter = ('status', )
    ordering = ('-create_time',)
    list_per_page = 10

    def tutor_user_name(self, obj):
        user_tutor_info = TutorInfo.objects.filter(id=obj.tutor_user_id).only('username').first()
        return user_tutor_info.username

    def student_user_name(self, obj):
        user_student_info = UserStudentInfo.objects.filter(id=obj.student_user_id).only('real_name').first()
        return user_student_info.real_name


class ScheduleTutorCourseAdmin(admin.ModelAdmin):

    list_display = ('id', 'tutor_user', 'course')
    search_fields = ('tutor_user__username', 'tutor_user__email', 'tutor_user__phone')


class ScheduleTutorClasstypeAdmin(admin.ModelAdmin):

    search_fields = ('tutor_user__username', 'tutor_user__phone', 'tutor_user__email')
    raw_id_fields = ('tutor_user', )
    list_display = ('id', 'tutor_user', 'class_type')


class ScheduleTutorLevelAdmin(admin.ModelAdmin):

    search_fields = ('tutor_user__username', 'tutor_user__email', 'tutor_user__phone')
    raw_id_fields = ('tutor_user', )
    list_display = ('id', 'tutor_user', 'course_edition', 'user_level')


class ScheduleVirtualclassMemberAdmin(admin.ModelAdmin):

    search_fields = ('virtual_class__id', )
    list_filter = ('first_course', )
    raw_id_fields = ('virtual_class', 'student_user', 'class_field', 'student_timetable')
    list_per_page = 10


@admin.register(TutorTimetable)
class TutorTimetableAdmin(admin.ModelAdmin):

    list_filter = ('status', )
    raw_id_fields = ('tutor_user', 'virtual_class', 'class_field', 'student_user')
    search_fields = ('id', )
    list_display = ('id', 'virtual_class_id', 'tutor_user_name', 'start_time', 'status')
    ordering = ('-create_time',)
    list_per_page = 10

    def tutor_user_name(self, obj):
        user_tutor_info = TutorInfo.objects.filter(id=obj.tutor_user_id).only('username').first()
        return user_tutor_info.username


admin.site.register(StudentTimetable, StudentTimetableAdmin)
admin.site.register(ScheduleTutorCourse, ScheduleTutorCourseAdmin)
admin.site.register(ScheduleTutorClasstype, ScheduleTutorClasstypeAdmin)
admin.site.register(ScheduleTutorLevel, ScheduleTutorLevelAdmin)
admin.site.register(ScheduleVirtualclassMember, ScheduleVirtualclassMemberAdmin)
