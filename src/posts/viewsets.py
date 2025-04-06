import base64
from typing import Any
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from django.db.models import QuerySet
from django.contrib.auth.models import AnonymousUser

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.decorators import action


from posts.models import Post, PostTypes
from posts.serializers import PostSerializer
from posts.permissions import PostPermission
from user_management.models import Node, Author

from core.utils.request_viewer import get_request_viewer
from core.utils.redirects import API_UNAUTHORIZED


class PostViewSet(viewsets.ModelViewSet[Post]):
    """ViewSet for handling posts (text & image)
       This viewset supports standard CRUD (read is auto handles by REST btw) Operations:

       - Create: attaches the current user's author instance w perform_create
       - Update: only allows authors to modify their own post
       - Destroy: performs soft delete instead of a hard delete
    """
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded uuid
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"
    lookup_value_regex = "[0-9a-fA-F-]{36}"
    queryset = Post.visible_posts.all()
    serializer_class = PostSerializer
    # permission_classes = [IsAuthenticated, PostPermission]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self) -> Post:
        """Allow for encoded uuid based lookup"""
        uuid = self.kwargs.get("uuid", None)
        if uuid is not None:
            lookup_field = "uuid"
            lookup_value = uuid
            return self.get_queryset().get(**{lookup_field: lookup_value})
        return super().get_object()

    @extend_schema(
        summary="List posts",
        description="Get a paginated list of all visible posts.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                description="Page number for pagination",
                required=False
            ),
            OpenApiParameter(
                name="size",
                type=int,
                description="Number of items per page",
                required=False
            )
        ],
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "example": "posts"},
                        "author": {
                            "type": "array",
                            "author": {"$ref": "#/components/schemas/Post"}
                        }
                    }
                },
                description="List of posts retrieved successfully"
            ),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=["Posts"]
    )
    def list(self, request: Request) -> Response:
        return super().list(request)

    @extend_schema(
        summary="Create post",
        description="Create a new post. The authenticated user will be the author.",
        request=PostSerializer,
        responses={
            201: PostSerializer,
            400: OpenApiResponse(description="Invalid post data"),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Posts"],
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override create to correctly attach author while allowing external nodes to create posts."""
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.is_user_node(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            print(request.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        author: Author = serializer.validated_data["author"]
        if not isinstance(author, Author):
            # This will be raised if I don't correctly understand the serializer, TODO: confirm this
            raise ValueError("validated_data[author] must be an instance of Author")

        # make sure the author is either the viewer, or the node viewing is the host of this author
        if viewer != author and not viewer_as_node:
            return Response(
                {"error": "You do not have permission to create a post for this author."},
                status=status.HTTP_403_FORBIDDEN
            )

        post = serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get post details",
        description="Get details of a specific post using its fully qualified ID (uuid)",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        responses={
            200: PostSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Posts"],
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update post (Full)",
        description="Fully update a post. All fields must be provided. Only the author can update their own posts.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        request=PostSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Invalid post data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Posts"],
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override update to ensure only authors can modify their posts"""
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.is_user_node(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        post: Post = self.get_object()

        # if the viewer is not the author, and the author is not hosted by the viewer, deny access
        if viewer != post.author and not viewer_as_node:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Update post (Partial)",
        description="Partially update a post. Only provided fields will be updated. Only the author can update their own posts.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        request=PostSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Invalid post data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Posts"],
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete post",
        description="Soft delete a post. Only the author can delete their own posts.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        responses={
            204: OpenApiResponse(description="Post successfully deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to delete this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Posts"],
    )
    def destroy(self, request: Request, **kwargs: Any) -> Response:
        """
        Soft delete the specified post.
        """
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.is_user_node(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        post: Post = self.get_object()

        if viewer != post.author and not viewer_as_node:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )


        post.soft_delete()
        # post._propagate_deletion_to_other_nodes()
        return Response({"detail": "Post soft deleted"}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get post image",
        description="Get the image of a post. Only available for image posts.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        responses={
            200: OpenApiResponse(description="Image retrieved successfully"),
            404: OpenApiResponse(description="Post not found or no image found"),
        },
        tags=["Posts"],
    )
    @action(detail=True, methods=["get"], url_path="image")
    def image(self, request: Request, uuid: str) -> Response:
        """
        GET Endpoint to retrieve a binary image from a post.
        """
        post = self.get_object()

        if post.post_type != PostTypes.IMAGE or not post.image:
            return Response({"error": "No image post found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            image_file = post.image.open("rb")
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception:
            return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(encoded_image, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get post video",
        description="Get the video of a post. Only available for video posts.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post",
            )
        ],
        responses={
            200: OpenApiResponse(description="Video retrieved successfully"),
            404: OpenApiResponse(description="Post not found or no video found"),
        },
        tags=["Posts"],
    )
    @action(detail=True, methods=["get"], url_path="video")
    def video(self, request: Request, uuid: str) -> Response:
        """
        GET Endpoint to retrieve a binary video from a post.
        """
        post = self.get_object()

        if post.post_type != PostTypes.VIDEO or not post.video:
            return Response({"error": "No video post found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            video_file = post.video.open("rb")
            encoded_video = base64.b64encode(video_file.read()).decode("utf-8")
        except Exception:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(encoded_video, status=status.HTTP_200_OK)

class AuthorPostViewSet(viewsets.ModelViewSet[Post]):
    serializer_class = PostSerializer
    lookup_url_kwarg = "post_uuid"

    def get_queryset(self) -> QuerySet[Post]:
        author_uuid = self.kwargs.get("author_uuid")
        return Post.objects.filter(author__uuid=author_uuid)
