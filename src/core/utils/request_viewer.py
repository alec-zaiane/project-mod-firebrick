from django.http import HttpRequest
from user_management.models import Author, LocalAuthor, Node
from typing import Optional


def get_request_viewer(request: HttpRequest) -> Optional[LocalAuthor]:
    """Get the viewing Author from the request object"""
    if not request.user.is_authenticated:
        return None
    return Author.local_authors.find_author_with_user(request.user)


def get_request_node(request: HttpRequest) -> Optional[Node]:
    """Get the viewing Node from the request object"""
    if not request.user.is_authenticated:
        return None
    return Node.objects.filter(internal_user=request.user).first()
