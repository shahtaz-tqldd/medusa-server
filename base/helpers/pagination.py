from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class CustomPagination(PageNumberPagination):
    """
    Custom pagination
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DynamicPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100