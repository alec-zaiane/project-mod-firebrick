from typing import Optional

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.shortcuts import get_object_or_404
from user_management.models import Author


from posts.models import Post
from comments.models import Comment
from likes.models import Like

from core.utils.request_viewer import get_request_viewer
from likes.serializers import LikeSerializer

from uuid import UUID

# Create your views here.


class LikeByViewer(APIView):

    @extend_schema(
        operation_id="create_like_by_viewer",
        summary="[Internal] Create like for post/comment",
        description="Create a like for a post or comment by the authenticated viewer. Acts as a toggle - if the viewer has already liked the target, the like will be removed.",
        parameters=[
            OpenApiParameter(
                name="target_fqid",
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post/comment to like/unlike",
                required=True,
                type=str,
            ),
        ],
        responses={
            201: OpenApiResponse(description="Like created or toggled successfully"),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Log in as a user to like a post or comment",
                        }
                    },
                },
            ),
            404: OpenApiResponse(
                description="Target not found",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Could not find post or comment with id {target_fqid}",
                        }
                    },
                },
            ),
        },
        tags=["Likes"],
    )
    def post(self, request: Request, target_fqid: str) -> Response:
        """Create a like for a post or comment by the viewer.
        Cannot create a like for a post or comment that has already been liked by the viewer.
        """
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response({"error": "Log in as a user to like a post or comment"}, status=401)

        maybe_post = Post.visible_posts.find_by_encoded_fqid(target_fqid)
        maybe_comment = Comment.objects.find_by_encoded_fqid(target_fqid)
        target: Optional[Post | Comment] = maybe_post or maybe_comment

        if target is None:
            return Response({"error": f"Could not find post or comment with id {target_fqid}"}, status=404)
        if target.likes.filter(author=viewer).exists():
            Like.objects.remove_like(viewer, target, target.likes.get(author=viewer))
            return Response(status=201)
        Like.objects.create_like(viewer, target)
        return Response(status=201)

    @extend_schema(
        operation_id="delete_like_by_viewer",
        summary="[Internal] Delete like from post/comment",
        description="Delete a like from a post or comment by the authenticated viewer. Cannot delete a like that hasn't been created.",
        parameters=[
            OpenApiParameter(
                name="target_fqid",
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the post/comment to unlike",
                required=True,
                type=str,
            ),
        ],
        responses={
            204: OpenApiResponse(description="Like deleted successfully"),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Log in as a user to unlike a post or comment",
                        }
                    },
                },
            ),
            404: OpenApiResponse(
                description="Like not found",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "You have not liked this post or comment",
                        }
                    },
                },
            ),
        },
        tags=["Likes"],
    )
    def delete(self, request: Request, target_fqid: str) -> Response:
        """Delete a like for a post or comment by the viewer.
        Cannot delete a like for a post or comment that has not been liked by the viewer.
        """
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response({"error": "Log in as a user to unlike a post or comment"}, status=401)

        maybe_post = Post.visible_posts.find_by_encoded_fqid(target_fqid)
        maybe_comment = Comment.objects.find_by_encoded_fqid(target_fqid)
        target: Optional[Post | Comment] = maybe_post or maybe_comment

        if target is None:
            return Response({"error": f"Could not find post or comment with id {target_fqid}"}, status=404)
        if not target.likes.filter(author=viewer).exists():
            return Response({"error": "You have not liked this post or comment"}, status=404)
        target.likes.filter(author=viewer).delete()
        return Response(status=204)


class AuthorLikesAPIView(APIView):
    """API endpoint that returns all likes by an author, used for node synchronization"""
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, author_uuid: UUID) -> Response:
        author = Author.local_authors.find_by_uuid(author_uuid)
        if author is None:
            return Response({"detail": "author not found"}, status=404)

        likes = Like.objects.filter(author=author)
        serializer = LikeSerializer(likes, many=True)
        return Response({
            "type": "likes",
            "src": serializer.data
        })
