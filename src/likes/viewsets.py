
from typing import Any

from rest_framework import viewsets
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from likes.models import Like
from likes.serializers import LikeSerializer
from user_management.models import Author, Node
from user_management.serializers import AuthorSerializer


class LikeViewSet(viewsets.ModelViewSet[Like]):
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded fqid
    lookup_field = "fqid"
    lookup_url_kwarg = "fqid"
    lookup_value_regex = ".+"
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    # TODO custom permission class

    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]
        return Response({
            "type": "likes",
            "items": super_data
        })

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def destroy(self, request: Request, pk: str) -> Response:
        like = self.get_object()
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
