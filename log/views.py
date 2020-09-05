from rest_framework import viewsets
from manager.log.serializer import ManagerLogSerializer
from manager.pagination import LargeResultsSetPagination
from manager.log.models import ManagerLog
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from manager.log.filters import ManagerLogFilterBackend, ManagerLogFilter
import logging

logger = logging.getLogger(__name__)


class OperationLogViewSet(viewsets.ModelViewSet):

    serializer_class = ManagerLogSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, ManagerLogFilterBackend, filters.OrderingFilter)
    filter_class = ManagerLogFilter
    pagination_class = LargeResultsSetPagination
    queryset = ManagerLog.objects.all()
