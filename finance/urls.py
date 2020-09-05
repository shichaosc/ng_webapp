from finance.views import RechargeViewSet, AttendClassInfoViewSet, \
    StatisticsViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'recharge', RechargeViewSet, base_name='recharge')
router.register(r'attendclassinfo', AttendClassInfoViewSet, base_name='attendclassinfo')
router.register(r'statistic', StatisticsViewSet, base_name='statistic')


urlpatterns = [
    url(r'', include(router.urls)),
]

