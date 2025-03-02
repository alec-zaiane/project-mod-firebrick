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
- URL:`://service/api/authors/{AUTHOR_SERIAL}/inbox`
    - `POST`[remote]: send a like object to`AUTHOR_SERIAL`
    - Body is [like object]
- URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes`
    - "Who Liked This Post"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
- URL:`://service/api/posts/{POST_FQID}/likes`
    - "Who Liked This Post"
    - `GET`[local] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
- URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes`
    - "Who Liked This Comment"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`comment`COMMENT_FQID`
    - Body is [likes object]
"""

# URL:`://service/api/authors/{AUTHOR_SERIAL}/inbox` needs an InboxHandler


class LikesInboxHandler(InboxHandler):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/inbox`
        - `POST`[remote]: send a like object to`AUTHOR_SERIAL`
        - Body is [like object]
    """

    def __init__(self) -> None:
        super().__init__(["like"])

    def post(self, request: Request) -> Response:
        raise NotImplementedError("TODO")


register_inbox_handler(LikesInboxHandler())


class LikesOnPostBySerialView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes`
    - "Who Liked This Post"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str) -> Response:
        raise NotImplementedError("TODO")


class LikesOnPostByFqidView(views.APIView):
    """
    - URL:`://service/api/posts/{POST_FQID}/likes`
    - "Who Liked This Post"
    - `GET`[local] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, post_fqid: str) -> Response:
        raise NotImplementedError("TODO")


class LikesOnCommentView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes`
    - "Who Liked This Comment"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`comment`COMMENT_FQID`
    - Body is [likes object]
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, comment_fqid: str) -> Response:
        raise NotImplementedError("TODO")
