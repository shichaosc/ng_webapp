from activity.views import GroupActivityViewSet, GroupRechargeViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'group_activity', GroupActivityViewSet, base_name='group_activity')
router.register(r'group_recharge', GroupRechargeViewSet, base_name='group_recharge')


urlpatterns = [
    url(r'activity/', include(router.urls)),
]
