from typing import Any

from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError

from comments.serializers import CommentSerializer
from comments.models import Comment

from urllib.parse import unquote


class CommentViewSet(viewsets.ModelViewSet[Comment]):
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded uuid
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"
    lookup_value_regex = ".+"
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_object(self) -> Comment:
        """Allow for encoded uuid based lookup"""
        uuid = self.kwargs.get("uuid", None)
        if uuid is not None:
            lookup_field = "uuid"
            lookup_value = unquote(uuid)
            return self.get_queryset().get(**{lookup_field: lookup_value})
        return super().get_object()

    @extend_schema(
        summary="List comments",
        description="Get a list of all comments. Results are paginated.",
        responses={
            200: CommentSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Comments"],
    )
    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]
        return Response({
            "type": "comments",
            "author": super_data
        })

    @extend_schema(
        summary="Create comment",
        description="Create a new comment on a post.",
        request=CommentSerializer,
        responses={
            201: OpenApiResponse(
                response=CommentSerializer, description="Comment created successfully"
            ),
            400: OpenApiResponse(description="Invalid comment data"),
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Comments"],
    )
    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "malformed comment", "comment": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        validated_data: dict[str, Any] = serializer.validated_data
        comment = serializer.create(validated_data)
        return Response(serializer.to_representation(comment), status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get comment details",
        description="Get details of a specific comment using its fully qualified ID (uuid)",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the comment",
            )
        ],
        responses={
            200: CommentSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Comment not found"),
        },
        tags=["Comments"],
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update comment (Full)",
        description="Fully update a comment. All fields must be provided.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the comment",
            )
        ],
        request=CommentSerializer,
        responses={
            200: CommentSerializer,
            400: OpenApiResponse(description="Invalid comment data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this comment"),
            404: OpenApiResponse(description="Comment not found"),
        },
        tags=["Comments"],
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Update comment (Partial)",
        description="Partially update a comment. Only provided fields will be updated.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the comment",
            )
        ],
        request=CommentSerializer,
        responses={
            200: CommentSerializer,
            400: OpenApiResponse(description="Invalid comment data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this comment"),
            404: OpenApiResponse(description="Comment not found"),
        },
        tags=["Comments"],
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().partial_update(request, *args, **kwargs)

    # Documents the delete operation for comments, including authentication requirements and possible responses
    @extend_schema(
        summary="Delete a comment",
        description="Delete a comment. Only the comment author can delete their own comments.",
        responses={
            204: OpenApiResponse(description="Comment successfully deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to delete this comment"),
            404: OpenApiResponse(description="Comment not found"),
        },
        tags=["Comments"],
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().destroy(request, *args, **kwargs)
