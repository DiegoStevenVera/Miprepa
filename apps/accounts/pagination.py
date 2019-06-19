from rest_framework.pagination import PageNumberPagination


class TenUserPagination(PageNumberPagination):
    page_size = 10


class PaginateBy50(PageNumberPagination):
    page_size = 50
