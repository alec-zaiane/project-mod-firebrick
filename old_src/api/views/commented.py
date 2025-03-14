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
        summary="Get the list of comments by an author (paginated)",
        responses=serializers.CommentsSerializer,
        parameters=[
            OpenApiParameter("author_uuid_or_fqid", type=str,
                             location=OpenApiParameter.PATH, description="Either the UUID or FQID of the author"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid_or_fqid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        # TODO Must be able to handle both AUTHOR_SERIAL and AUTHOR_FQID
        raise NotImplementedError("TODO")

    @extend_schema(
        summary="Post a comment by this author",
        description="Post a Comment object, must be authenticated as this author",
        request=serializers.CommentSerializer,
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author posting the comment")
        ]
    )
    @method_decorator(user_controller())
    def post(self, request: Request, author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        viewer_is_author = getattr(viewer, "uuid", None) == author_uuid
        user_control(request, verify_true=viewer_is_author)
        raise NotImplementedError("TODO")


class CommentedBySerialView(views.APIView):
    """
    URL: ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    - GET [local, remote] get this comment
    """

    @extend_schema(
        summary="Get a comment by an author",
        responses=serializers.CommentSerializer,
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author who made the comment"),
            OpenApiParameter("comment_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the comment")
        ]
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
        summary="Get a comment by FQID",
        responses=serializers.CommentSerializer,
        parameters=[
            OpenApiParameter("comment_fqid", type=str, location=OpenApiParameter.PATH,
                             description="The FQID of the comment (percent encoded)")
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, comment_fqid: str) -> Response:
        raise NotImplementedError("TODO")
