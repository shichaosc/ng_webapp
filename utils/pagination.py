from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import Response
import math


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):

        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page_count': math.ceil(self.page.paginator.count/self.page.paginator.per_page),
            'page_size': self.page.paginator.per_page,
            'results': data
        })


class TeacherPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):

        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page_count': math.ceil(self.page.paginator.count/self.page_size),
            'page_size': self.page_size,
            'results': data
        })
