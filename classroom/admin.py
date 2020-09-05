from django.contrib import admin
from classroom.models import ClassInfo, ClassMember, ClassType, VirtualclassComment, \
    VirtualclassInfo, VirtualclassResource, VirtualclassType, VirtualclassHomeworkResult, \
    VirtualclassHomeworkAttachment, VirtualclassException
from tutor.models import TutorInfo
from student.models import UserStudentInfo
from finance.models import BalanceChange
from classroom.forms import VirtualclassExceptionForm


@admin.register(VirtualclassInfo)
class VirtualclassInfoAdmin(admin.ModelAdmin):

    list_display = ('id', 'tutor_user_name', 'start_time', 'tk_class_id', 'status', 'reason', 'class_type_id')
    search_fields = ('id', )
    list_filter = ('reason', 'status', 'first_course')
    raw_id_fields = ('tutor_user', 'lesson', 'class_field', 'student_user', )
    ordering = ('-start_time', )
    list_per_page = 10

    def tutor_user_name(self, obj):
        user_tutor_info = TutorInfo.objects.filter(id=obj.tutor_user_id).only('username').first()
        return user_tutor_info.username


@admin.register(VirtualclassResource)
class VirtualclassResourceAdmin(admin.ModelAdmin):

    search_fields = ('virtual_class__tutor_user__username', 'virtual_class__tutor_user__email', 'virtual_class__tutor_user__phone')
    list_display = ('id', 'virtual_class_id', 'ext_course', 'create_time')
    raw_id_fields = ('virtual_class', 'ext_course', )
    ordering = ('-create_time',)
    list_per_page = 10


@admin.register(ClassInfo)
class ClassInfoAdmin(admin.ModelAdmin):

    search_fields = ('class_member__student_user__real_name', )
    list_display = ('id', 'user_num', 'class_name_zh')
    raw_id_fields = ('lesson', 'creator_user', 'leader_user')

    list_per_page = 10

    def class_type(self, class_info):
        return ClassType.objects.get(id=class_info.class_type_id)


@admin.register(ClassMember)
class ClassMemberAdmin(admin.ModelAdmin):

    list_filter = ('role', )
    raw_id_fields = ('class_field', 'student_user')
    list_display = ('id', 'class_field', 'student_user_name', 'role', 'parent_user_name')
    list_per_page = 10

    def student_user_name(self, obj):
        user_student_info = UserStudentInfo.objects.filter(id=obj.student_user_id).only('real_name').first()
        return user_student_info.real_name

    def parent_user_name(self, obj):
        user_student_info = UserStudentInfo.objects.filter(id=obj.student_user_id).only('parent_user__username').first()
        return user_student_info.real_name


@admin.register(VirtualclassComment)
class VirtualclassComentAdmin(admin.ModelAdmin):

    search_fields = ('tutor_user__username', 'tutor_user__email', 'tutor_user__phone')
    list_filter = ('role',)
    list_display = ('id', 'role', 'tutor_user_name', 'student_user_name', 'virtual_class_id')
    raw_id_fields = ('student_user', 'tutor_user', 'virtual_class')
    ordering = ('-create_time',)
    list_per_page = 10

    def tutor_user_name(self, obj):
        user_tutor_info = TutorInfo.objects.filter(id=obj.tutor_user_id).only('username').first()
        return user_tutor_info.username

    def student_user_name(self, obj):
        user_student_info = UserStudentInfo.objects.filter(id=obj.student_user_id).only('real_name').first()
        return user_student_info.real_name


@admin.register(VirtualclassHomeworkResult)
class VirtualclassHomeworkResultAdmin(admin.ModelAdmin):

    list_display = ('id', 'tutor_user_name', 'student_user_name', 'score', 'virtual_class_id')
    raw_id_fields = ('student_user', 'tutor_user')
    search_fields = ('student_user__real_name', )
    list_per_page = 10

    def tutor_user_name(self, obj):
        user_tutor_info = TutorInfo.objects.filter(id=obj.tutor_user_id).only('username').first()
        return user_tutor_info.username

    def student_user_name(self, obj):
        user_student_info = UserStudentInfo.objects.filter(id=obj.student_user_id).only('real_name').first()
        return user_student_info.real_name


@admin.register(VirtualclassHomeworkAttachment)
class VirtualclassHomeworkAttachmentAdmin(admin.ModelAdmin):

    list_filter = ('attachment_type', )
    raw_id_fields = ('virtual_class', 'homework_result')
    search_fields = ('homework_result__student_user__real_name', )
    list_display = ('id', 'attachment_type', 'attachment', 'virtual_class_id', 'homework_result_id')
    list_per_page = 10


@admin.register(VirtualclassException)
class VirtualclassExceptionAdmin(admin.ModelAdmin):

    form = VirtualclassExceptionForm
    llist_display = ('id', 'cms_user', 'result', 'description', 'balance_result')
    list_per_page = 10
    list_filter = ('result', )
    search_fields = ('vitual_class_id', )

    def balance_result(self, virtualclass_exception):
        virtual_class_id = virtualclass_exception.virtual_class_id
        balance_changes = BalanceChange.objects.filter(reference=virtual_class_id).all()
        result = []
        for balance_change in balance_changes:
            result.append(balance_change.__str__())
        return '|'.join(result)


admin.site.register(ClassType)
admin.site.register(VirtualclassType)


