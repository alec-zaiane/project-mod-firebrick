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

"""Commented API from the class docs:

URL: ://service/api/authors/{AUTHOR_SERIAL}/commented
- GET [local, remote] get the list of comments author has made on:
    - [local] any post
    - [remote] public and unlisted posts
    - paginated
- POST [local] if you post an object of "type":"comment", it will add your comment to the post whose ID is in the post field
    - Then the node you posted it to is responsible for forwarding it to the correct inbox
URL: ://service/api/authors/{AUTHOR_FQID}/commented
    - GET [local] get the list of comments author has made on any post (that local node knows about)

URL: ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    - GET [local, remote] get this comment
URL: ://service/api/commented/{COMMENT_FQID}
    - GET [local] get this comment
"""


class CommentedAuthorView(views.APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/commented
    - GET [local, remote] get the list of comments author has made on:
        - [local] any post
        - [remote] public and unlisted posts
        - paginated
    - POST [local] if you post an object of "type":"comment", it will add your comment to the post whose ID is in the post field
        - Then the node you posted it to is responsible for forwarding it to the correct inbox
    URL: ://service/api/authors/{AUTHOR_FQID}/commented
        - GET [local] get the list of comments author has made on any post (that local node knows about)
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid_or_fqid: str) -> Response:
        # TODO Must be able to handle both AUTHOR_SERIAL and AUTHOR_FQID
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def post(self, request: Request, author_uuid: str) -> Response:
        raise NotImplementedError("TODO")


class CommentedBySerialView(views.APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    - GET [local, remote] get this comment
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, comment_uuid: str) -> Response:
        raise NotImplementedError("TODO")


class CommentedFqidView(views.APIView):
    """
    URL: ://service/api/commented/{COMMENT_FQID}
    - GET [local] get this comment
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, comment_fqid: str) -> Response:
        raise NotImplementedError("TODO")
