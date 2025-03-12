"""This file contains factory functions for creating test data"""
from typing import Optional, Any
from user_management.models import Author, Node, JoinRequest, LocalAuthor, ExternalAuthor
from user_management.serializers import AuthorSerializer


def create_dummy_join_request(username: str, email: str, display_name: Optional[str] = None, password: str = "password") -> JoinRequest:
    if display_name is None:
        display_name = username
    return JoinRequest.objects.create_join_request(username=username, email=email, display_name=display_name, password=password)


def create_dummy_local_author(username: str, email: str, display_name: Optional[str] = None, password: str = "password") -> LocalAuthor:
    if display_name is None:
        display_name = username
    join_request = create_dummy_join_request(username, email, display_name, password)
    author = join_request.approve()
    return author


def create_dummy_external_author(username: str, email: str, host: Node, display_name: Optional[str] = None) -> ExternalAuthor:
    if display_name is None:
        display_name = username
    return Author.external_authors.create(username=username, display_name=display_name, host_node=host)


class DummyJsonObjectGenerator:
    """Generate dummy objects in `dict` form"""

    @staticmethod
    def followrequest(follower: Author, followee: Author) -> dict[str, Any]:
        raise NotImplementedError()
