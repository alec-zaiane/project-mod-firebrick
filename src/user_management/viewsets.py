from rest_framework import viewsets

from rest_framework.request import Request
from rest_framework.response import Response

from user_management.models import Author
from user_management.serializers import AuthorSerializer


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]  # fix for pagination
        return Response({
            "type": "authors",
            "items": super_data
        })
