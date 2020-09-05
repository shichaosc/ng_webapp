
from course.views import CourseEditionViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'course_edition', CourseEditionViewSet, base_name='course_edition')

urlpatterns = [
    url(r'', include(router.urls)),
]
