"""Handles permissions for posts (for DRF serializers and views)"""
# https://www.django-rest-framework.org/api-guide/permissions/

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from posts.models import Post
from user_management.models import User, Author


class PostPermission(BasePermission):
    """Custom permissions for posts"""

    def has_object_permission(self, request: Request, view: APIView, post: Post) -> bool:
        """Check if the user has permission to access the post
        Viewing a post is determined by the posts's visibility settings
        Editing a post is restricted to the author or host node
        """
        if request.method in SAFE_METHODS:
            viewer = User.objects.get(pk=request.user.pk)
            if viewer.type == User.Types.NODE:
                # only let the host node of a post view it (other nodes shouldn't be asking us for this post, but should be asking the host node)
                return post.host_node.internal_user == viewer
            else:
                # check for visibility
                author = Author.objects.get(pk=post.author.pk)
                return post.check_can_be_seen_by(author)
        else:
            return post.author.user == request.user or post.host_node.internal_user == request.user
