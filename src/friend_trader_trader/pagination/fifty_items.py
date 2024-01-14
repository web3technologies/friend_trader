from rest_framework.pagination import PageNumberPagination


class FiftyItemsPagination(PageNumberPagination):
    page_size = 50