from homework.views import HomeworkKnowledgeViewSet, HomeworkOutlineGroupViewSet, \
    HomeworkQuestionViewSet, HomeworkOutlineInfoViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'knowledge', HomeworkKnowledgeViewSet, base_name='knowledge')
router.register(r'outline_group', HomeworkOutlineGroupViewSet, base_name='outline_group')
router.register(r'outline', HomeworkOutlineInfoViewSet, base_name='outline')
router.register(r'question', HomeworkQuestionViewSet, base_name='homework_question')

urlpatterns = [
    url(r'homework/', include(router.urls)),
]
