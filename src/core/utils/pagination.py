from rest_framework import pagination

# https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles


class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    page_query_param = "page"
