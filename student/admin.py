from django.contrib import admin
from student.models import UserStudentInfo, UserParentInfo, UserSocialToken, UserSocialApp, UserSocialAccount, \
    AdData
from django.db.models import Q


@admin.register(UserParentInfo)
class UserParentinfoAdmin(admin.ModelAdmin):

    list_filter = ('status', )
    search_fields = ('username', 'email', 'phone')
    list_per_page = 50


@admin.register(UserStudentInfo)
class UserStudentInfoAdmin(admin.ModelAdmin):

    list_filter = ('assessed', )
    raw_id_fields = ('parent_user', 'student_parent_user', 'lesson')
    list_display = ('id', 'real_name', )
    search_fields = ('parent_name', )
    list_per_page = 20

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(Q(parent_user__username=search_term) | Q(parent_user__email=search_term) | Q(
                parent_user__phone=search_term))
        return queryset, use_distinct


@admin.register(AdData)
class AdDataAdmin(admin.ModelAdmin):

    raw_id_fields = ('parent_user', )


admin.site.register(UserSocialToken)
admin.site.register(UserSocialApp)
admin.site.register(UserSocialAccount)
