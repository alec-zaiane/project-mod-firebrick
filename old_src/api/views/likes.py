from typing import Optional

from itertools import chain

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

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
        super().__init__("like")

    @property
    def serializer(self) -> type[serializers.LikeSerializer]:
        return serializers.LikeSerializer

    def post(self, request: Request, viewer: Optional[models.LocalAuthor] = None) -> Response:
        serializer = serializers.LikeSerializer(data=request.data)
        if viewer is None:
            return Response("User must be authenticated", status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            # double check that the author has access to the target object
            like_target = serializer.get_target()
            if isinstance(like_target, models.Post):
                user_control(
                    request, verify_true=like_target.check_can_be_seen_by(viewer))
            elif isinstance(like_target, models.Comment):
                user_control(
                    request, verify_true=like_target.check_can_be_seen_by(viewer))

            like = serializer.create(serializer.validated_data)
            return Response({
                "detail": "Like Created",
                "like": serializers.LikeSerializer(like).data
            }, status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "Invalid Like",
                "like": serializer.errors
            }, status.HTTP_400_BAD_REQUEST)


register_inbox_handler(LikesInboxHandler())


class LikesOnPostBySerialView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes`
    - "Who Liked This Post"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
    """

    @extend_schema(
        summary="Get a list of likes on a post",
        description="Get a list of likes on a post by AUTHOR_UUID and POST_UUID (Paginated)",
        responses=serializers.LikesSerializer,
        parameters=[
            OpenApiParameter("author_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of the author"),
            OpenApiParameter("post_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of their post"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


class LikesOnPostByFqidView(views.APIView):
    """
    - URL:`://service/api/posts/{POST_FQID}/likes`
    - "Who Liked This Post"
    - `GET`[local] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`
    - Body is [likes object]
    """

    @extend_schema(
        summary="Get a list of likes on a post",
        description="Get a list of likes on a post by FQID (Paginated)",
        responses=serializers.LikesSerializer,
        parameters=[
            OpenApiParameter("post_fqid", str, OpenApiParameter.PATH,
                             description="The FQID of the post"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ],
    )
    @method_decorator(user_controller())
    def get(self, request: Request, post_fqid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


class LikesOnCommentView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes`
    - "Who Liked This Comment"
    - `GET`[local, remote] a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`comment`COMMENT_FQID`
    - Body is [likes object]
    """

    @extend_schema(
        summary="Get a list of likes on a comment",
        description="Get  a list of likes from other authors on`AUTHOR_SERIAL`'s post`POST_SERIAL`comment`COMMENT_FQID`",
        responses=serializers.LikesSerializer,
        parameters=[
            OpenApiParameter("author_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of the author"),
            OpenApiParameter("post_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of their post"),
            OpenApiParameter("comment_fqid", str, OpenApiParameter.PATH,
                             description="The FQID of the comment"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ]

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, comment_fqid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


# INTERNAL

class LikePostInternalView(views.APIView):
    @extend_schema(
        summary="As a local author, like a post",
        description="Like a post by POST_UUID",
        request=None,
        responses={201: "Success", 400: "Bad Request",
                   401: "Unauthorized", 403: "Forbidden"},
        parameters=[
            OpenApiParameter("post_uuid", str, OpenApiParameter.PATH,
                             description="The UUID of the local post to like"),
        ]
    )
    @method_decorator(user_controller(must_be_logged_in=True, must_be_author=True))
    def post(self, request: Request, post_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        if viewer is None:
            return Response("User must be authenticated", status.HTTP_401_UNAUTHORIZED)
        text_maybe = models.PostTextBased.objects.filter(
            uuid=post_uuid).first()
        image_maybe = models.PostMediaBased.objects.filter(
            uuid=post_uuid).first()
        if text_maybe is None and image_maybe is None:
            return Response("Post not found", status.HTTP_404_NOT_FOUND)
        post = text_maybe or image_maybe
        assert post is not None  # for mypy
        post_diff = models.PostDifferentiator.create_differentiator_for_post(
            post)
        like = models.Like.objects.create(
            author=viewer, target_post_differentiator=post_diff)
        return Response(status=200)
