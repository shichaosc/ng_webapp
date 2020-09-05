from django.contrib import admin
from django.db.models import Q
from activity.models import ActivityBannerInfo, ActivityMessageInfo
from tutor.models import TutorInfo
from student.models import UserParentInfo, UserStudentInfo
from ambassador.models import UserAmbassadorInfo


@admin.register(UserAmbassadorInfo)
class AmbassadorAdmin(admin.ModelAdmin):

    list_filter = ('gender', 'default_account', 'status')
    search_fields = ('username', 'email', 'phone')
    list_display = ('id', 'username', 'email', 'phone', 'real_name', 'code', 'gender', 'default_account', 'status')
