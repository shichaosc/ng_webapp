from django.contrib import admin
from django.db.models import Q
from activity.models import ActivityBannerInfo, ActivityMessageInfo
from tutor.models import TutorInfo
from student.models import UserParentInfo, UserStudentInfo
from ambassador.models import UserAmbassadorInfo


@admin.register(ActivityBannerInfo)
class ActivityBannerInfoAdmin(admin.ModelAdmin):
    search_fields = ('name',)               # 指定要搜索的字段，将会出现一个搜索框让管理员搜索关键词
    list_display = ('id', 'name', 'picture_url', 'route_type', 'route_url', 'status', 'create_time')
    ordering = ('-create_time',)
    list_filter = ('route_type',)     # 指定列表过滤器，右边将会出现一个快捷的日期过滤选项


@admin.register(ActivityMessageInfo)
class ActivityMessageInfoAdmin(admin.ModelAdmin):

    list_display = ('id', 'role', 'user', 'sub_category', 'detail', 'create_time')
    list_filter = ('role', 'sub_category')
    ordering = ('-create_time', )

    def user(self, activity_message):

        role = activity_message.role
        if role == ActivityMessageInfo.CHILDREN:
            student = UserStudentInfo.objects.filter(id=activity_message.user_id).first()
            return student
        elif role == ActivityMessageInfo.TEACHER:
            tutor = TutorInfo.objects.filter(id=activity_message.user_id).first()
            return tutor
        elif role == ActivityMessageInfo.PARENT:
            ambassador = UserAmbassadorInfo.objects.filter(id=activity_message.user_id).first()
            return ambassador
        elif role == ActivityMessageInfo.PARENT:
            parent = UserParentInfo.objects.filter(id=activity_message.user_id).first()
            return parent



