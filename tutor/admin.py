from django.contrib import admin
from django.db.models import Q
from tutor.models import TutorInfo


@admin.register(TutorInfo)
class TutorInfoAdmin(admin.ModelAdmin):

    list_filter = ('hide', 'working', 'status')
    search_fields = ('username', 'email', 'phone', 'real_name')
    list_per_page = 50
