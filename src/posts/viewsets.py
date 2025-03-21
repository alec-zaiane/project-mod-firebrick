from typing import Any, Optional

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.request import Request


from posts.models import Post
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

    queryset = Post.visible_posts.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, PostPermission]
    parser_classes = (MultiPartParser, FormParser)

    @login_required
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override create to correctly attach author while allowing external nodes to create posts."""
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.find_by_user(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author: Author = serializer.validated_data["author"]
        if not isinstance(author, Author):
            # This will be raised if I don't correctly understand the serializer, TODO: confirm this
            raise ValueError("validated_data[author] must be an instance of Author")

        # make sure the author is either the viewer, or the node viewing is the host of this author
        if viewer != author and author.host_node != viewer_as_node:
            return Response(
                {"error": "You do not have permission to create a post for this author."},
                status=status.HTTP_403_FORBIDDEN
            )

        post = serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)

    @login_required
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Override update to ensure only authors can modify their posts"""
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.find_by_user(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        post: Post = self.get_object()

        # if the viewer is not the author, and the author is not hosted by the viewer, deny access
        if viewer != post.author and post.author.host_node != viewer_as_node:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Soft delete the specified post.

        Instead of permanently deleting the post, this action marks the post as soft-deleted.
        Only the author of the post is allowed to do this.
        """
        if isinstance(request.user, AnonymousUser):
            return API_UNAUTHORIZED()
        viewer = get_request_viewer(request)
        viewer_as_node = Node.objects.find_by_user(request.user)
        if viewer is None and viewer_as_node is None:
            return API_UNAUTHORIZED()

        post: Post = self.get_object()

        # if the viewer is not the author, and the author is not hosted by the viewer, deny access
        if viewer != post.author and post.author.host_node != viewer_as_node:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )

        post.soft_delete()
        return Response({"detail": "Post soft deleted"}, status=status.HTTP_204_NO_CONTENT)
