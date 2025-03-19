"""Handles permissions for user management classes (for DRF serializers and views)"""
# https://www.django-rest-framework.org/api-guide/permissions/

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from user_management.models import Author


class AuthorPermission(BasePermission):
    """Custom permissions for posts"""

    def has_object_permission(self, request: Request, view: APIView, author: Author) -> bool:
        """Check if the user has permission to access the author
        Anyone can view an author, but only themselves or their host node can edit them
        """
        if request.method in SAFE_METHODS:
            return True
        else:
            return author.user == request.user or author.host_node.internal_user == request.user
