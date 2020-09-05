
from student.views import StudentManagerViewSet, OldStudentManagerViewSet, \
    ExtStudentViewSet, RemarkViewSet, SmallClassStudentViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'student', StudentManagerViewSet, base_name='manager_student')
router.register(r'warn/student', StudentManagerViewSet, base_name='manager_student')
router.register(r'oldstudent', OldStudentManagerViewSet, base_name='manager_old_student')
router.register(r'extstudent', ExtStudentViewSet, base_name='manager_extstudent')
router.register(r'remarkstudent', RemarkViewSet, base_name='manager_student_remark')
# router.register(r'download/student', WarnStudentDownload, base_name='warn_student_download')
router.register(r'smallclass_student', SmallClassStudentViewSet, base_name='smallclass_student')


urlpatterns = [
    url(r'', include(router.urls)),
]

