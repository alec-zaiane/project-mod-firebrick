from typing import Any

from rest_framework import viewsets, status

from rest_framework.request import Request
from rest_framework.response import Response

from comments.serializers import CommentSerializer
from comments.models import Comment


class CommentViewSet(viewsets.ModelViewSet[Comment]):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

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
