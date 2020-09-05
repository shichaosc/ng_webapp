from unit_report.views import UnitReportViewSet, FirstReportViewSet
from django.conf.urls import url, include
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'unit_report', UnitReportViewSet, base_name='unit_report')
router.register(r'first_report', FirstReportViewSet, base_name='first_report')


urlpatterns = [
    url(r'', include(router.urls)),
]
