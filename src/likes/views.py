from typing import Optional

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from posts.models import Post
from comments.models import Comment
from likes.models import Like

from core.utils.request_viewer import get_request_viewer

# Create your views here.


class LikeByViewer(APIView):
    @extend_schema(
        summary="[Internal] create a like for a post or comment by the viewer",
        description="Create a like for a post or comment by the viewer. Cannot create a like for a post or comment that has already been liked by the viewer.",
        responses={201: None, 400: None, 401: None, 404: None},
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
        summary="[Internal] delete a like for a post or comment by the viewer",
        description="Delete a like for a post or comment by the viewer. Cannot delete a like for a post or comment that has not been liked by the viewer.",
        responses={204: None, 401: None, 404: None},
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
