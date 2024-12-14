from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 32
    max_page_size = 128

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.page.number + 1 if self.page.has_next() else None,
                "previous": self.page.number - 1 if self.page.has_previous() else None,
                "data": data,
            }
        )
