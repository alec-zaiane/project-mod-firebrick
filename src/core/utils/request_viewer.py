from django.http import HttpRequest
from user_management.models import Author, LocalAuthor
from typing import Optional


def get_request_viewer(request: HttpRequest) -> Optional[LocalAuthor]:
    """Get the viewer from the request object"""
    if not request.user.is_authenticated:
        return None
    return Author.local_authors.find_author_with_user(request.user)
