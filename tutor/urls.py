from tutor.views import FilterTeacherViewSet, TeacherMatchViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'filter_teacher', FilterTeacherViewSet, base_name='filter_teacher')
router.register(r'teacher_match', TeacherMatchViewSet, base_name='teacher_match')


urlpatterns = [
    url(r'', include(router.urls)),
]
