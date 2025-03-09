from typing import Optional

from itertools import chain

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from socialnetwork.utils.user_control_decorator import user_controller, user_control
from socialnetwork.utils.get_object_by_fqid import get_object_by_fqid, differentiate_id
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
        super().__init__("comment")

    @property
    def serializer(self) -> type[serializers.CommentSerializer]:
        return serializers.CommentSerializer

    def post(self, request: Request, viewer: Optional[models.LocalAuthor] = None) -> Response:
        serializer = serializers.CommentSerializer(data=request.data)
        if viewer is None:
            return Response("User must be authenticated", 401)
        if serializer.is_valid():
            # double check that the viewer has access to the target object
            try:
                target = get_object_by_fqid(serializer.validated_data["post"])
            except (SyntaxError, ObjectDoesNotExist):
                return Response("Target post is malformed", 404)
            if not isinstance(target, models.Post):
                return Response("Target post is not a post", 400)
            if not target.check_can_be_seen_by(viewer):
                return Response("Viewer does not have access to the target post", 403)
            comment = serializer.create(serializer.validated_data)
            return Response({"detail": "Comment created", "comment": serializer.data}, 201)
        return Response({"error": "Error creating comment", "comment": serializer.errors}, 400)


register_inbox_handler(CommentInboxHandler())


class CommentsSerialView(views.APIView):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
        - GET [local, remote]: the comments on the post
        - Body is a "comments" object
    """
    @extend_schema(
        description="Get the comments on a post",
        responses=serializers.CommentsSerializer,
        parameters=[
            OpenApiParameter("author_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of the author"),
            OpenApiParameter("post_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of their post"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ],
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, viewer: Optional[models.LocalAuthor]) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


class CommentsFqidView(views.APIView):
    """
    - URL: ://service/api/posts/{POST_FQID}/comments
        - GET [local, remote]: the comments on the post (that our server knows about)
        - Body is a "comments" object
    """
    @extend_schema(
        description="Get the comments on a post by FQID",
        responses=serializers.CommentsSerializer,
        parameters=[
            OpenApiParameter("post_fqid", str, OpenApiParameter.PATH,
                             description="The FQID of the post (percent encoded)"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, post_fqid: str, viewer: Optional[models.LocalAuthor]) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


class CommentsRemoteFqidView(views.APIView):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
        - GET [local, remote] get the comment
        - Example: GET http://nodebbbb/api/authors/222/posts/249/comments/http%3A%2F%2Fnodeaaaa%2Fapi%2Fauthors%2F111%2Fcommented%2F130:
    """
    @extend_schema(
        description="Get a remote comment on a local post by FQID",
        responses=serializers.CommentSerializer,
        parameters=[
            OpenApiParameter("author_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of the author"),
            OpenApiParameter("post_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of their post"),
            OpenApiParameter("comment_fqid", str, OpenApiParameter.PATH,
                             description="The FQID of the comment (percent encoded)")
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, comment_uuid_or_fqid: str) -> Response:
        raise NotImplementedError("TODO")
