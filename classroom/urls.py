from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken import views
from classroom.views import ClassroomViewSet, SmallclassVirtualclassViewSet, CommentViewSet
from classroom.class_views import ClassInfoViewSet, ClassTimeTableViewSet


router = routers.SimpleRouter()
router.register(r'classroom', ClassroomViewSet, base_name='classroom_list')
router.register(r'classinfo', ClassInfoViewSet, base_name='classinfo_list')
router.register(r'comment', CommentViewSet, base_name='comment_list')
router.register(r'class_timetable', ClassTimeTableViewSet, base_name='class_timetable')
router.register(r'smallclass/classroom', SmallclassVirtualclassViewSet, base_name='smallclass_virtualclass')


urlpatterns = [
    url(r'', include(router.urls)),
    # url(r'', include('manager.users.urls')),
    # url(r'', include('manager.student.urls')),
    url(r'^api-token-auth/', views.obtain_auth_token)
]
