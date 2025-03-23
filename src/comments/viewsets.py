from typing import Any

from rest_framework import viewsets, status

from rest_framework.request import Request
from rest_framework.response import Response

from comments.serializers import CommentSerializer
from comments.models import Comment

from urllib.parse import unquote


class CommentViewSet(viewsets.ModelViewSet[Comment]):
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded fqid
    lookup_field = "fqid"
    lookup_url_kwarg = "fqid"
    lookup_value_regex = ".+"
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_object(self) -> Comment:
        """Allow for encoded fqid based lookup"""
        fqid = self.kwargs.get("fqid", None)
        if fqid is not None:
            lookup_field = "fqid"
            lookup_value = unquote(fqid)
            return self.get_queryset().get(**{lookup_field: lookup_value})
        return super().get_object()

    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]
        return Response({
            "type": "comments",
            "items": super_data
        })

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict[str, Any] = serializer.validated_data
        comment = serializer.create(validated_data)
        return Response(serializer.to_representation(comment), status=status.HTTP_201_CREATED)
