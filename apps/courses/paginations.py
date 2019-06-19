from rest_framework.pagination import PageNumberPagination


class TenSetPagination(PageNumberPagination):
    page_size = 1
