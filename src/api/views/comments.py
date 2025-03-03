from typing import Optional

from itertools import chain

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from socialnetwork.utils.user_control_decorator import user_controller, user_control
from socialnetwork import models
from api import serializers
from api.views.inbox import InboxHandler, register_inbox_handler

"""
Comments API
- URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
    - note: because this shares a URL with other inbox items, register an inbox.InboxHandler to respond to this
    - POST [remote]: comment on a post by AUTHOR_SERIAL
    - Body is a comment object
- URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
    - GET [local, remote]: the comments on the post
    - Body is a "comments" object
- URL: ://service/api/posts/{POST_FQID}/comments
    - GET [local, remote]: the comments on the post (that our server knows about)
    - Body is a "comments" object
- URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
    - GET [local, remote] get the comment
    - Example: GET http://nodebbbb/api/authors/222/posts/249/comments/http%3A%2F%2Fnodeaaaa%2Fapi%2Fauthors%2F111%2Fcommented%2F130:
"""

# URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox needs an InboxHandler


class CommentInboxHandler(InboxHandler):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
        - POST [remote]: comment on a post by AUTHOR_SERIAL
        - Body is a comment object
    """

    def __init__(self) -> None:
        super().__init__(["comment"])

    def post(self, request: Request) -> Response:
        raise NotImplementedError("TODO")


register_inbox_handler(CommentInboxHandler())


class CommentsSerialView(views.APIView):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
        - GET [local, remote]: the comments on the post
        - Body is a "comments" object
    """

    def get(self, request: Request, author_uuid: str, post_uuid: str) -> Response:
        raise NotImplementedError("TODO")


class CommentsFqidView(views.APIView):
    """
    - URL: ://service/api/posts/{POST_FQID}/comments
        - GET [local, remote]: the comments on the post (that our server knows about)
        - Body is a "comments" object
    """
    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, post_fqid: str) -> Response:
        raise NotImplementedError("TODO")


class CommentsRemoteFqidView(views.APIView):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
        - GET [local, remote] get the comment
        - Example: GET http://nodebbbb/api/authors/222/posts/249/comments/http%3A%2F%2Fnodeaaaa%2Fapi%2Fauthors%2F111%2Fcommented%2F130:
    """
    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, comment_fqid: str) -> Response:
        raise NotImplementedError("TODO")
