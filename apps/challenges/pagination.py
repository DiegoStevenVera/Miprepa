from rest_framework.pagination import PageNumberPagination


class TenPagination(PageNumberPagination):
    page_size = 10
