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

"""
- URL:`://service/api/authors/{AUTHOR_SERIAL}/liked`
    - "Things Liked By Author"
    - `GET`[local, remote] a list of likes by AUTHOR_SERIAL
    - Body is [likes object]
- URL:`://service/api/authors/{AUTHOR_FQID}/liked`
    - "Things Liked By Author"
    - `GET`[local] a list of likes by AUTHOR_FQID
    - Body is [likes object]
- URL:`://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}`
    - `GET`[local, remote] a single like
    - Body is [like object]
- URL:`://service/api/liked/{LIKE_FQID}`
    - `GET`[local] a single like
    - Body is [like object]
"""


class LikedByAuthorView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/liked`
        - "Things Liked By Author"
        - `GET`[local, remote] a list of likes by AUTHOR_SERIAL
        - Body is [likes object]
    - URL:`://service/api/authors/{AUTHOR_FQID}/liked`
        - "Things Liked By Author"
        - `GET`[local] a list of likes by AUTHOR_FQID
        - Body is [likes object]
    """

    @extend_schema(
        description="Get a list of likes by AUTHOR_SERIAL or AUTHOR_FQID (paginated)",
        responses=serializers.LikesSerializer,
        parameters=[
            OpenApiParameter("author_uuid_or_fqid", str, OpenApiParameter.PATH,
                             description="The author's UUID or FQID"),
            OpenApiParameter(
                "page", type=int, description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter(
                "size", type=int, description="How many comments per page", default=50),
        ],
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid_or_fqid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        # Remember to handle both AUTHOR_SERIAL and AUTHOR_FQID
        raise NotImplementedError("TODO")


class LikedByAuthorSpecificLikeView(views.APIView):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}`
    - `GET`[local, remote] a single like
    - Body is [like object]
    """
    @extend_schema(
        description="Get a single like by AUTHOR_UUID",
        responses=serializers.LikeSerializer,
        parameters=[
            OpenApiParameter("author_uuid", str, OpenApiParameter.PATH,
                             description="UUID of the author in question"),
            OpenApiParameter("like_uuid", str, OpenApiParameter.PATH,
                             description="UUID of the like in question"),
        ],
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, like_uuid: str) -> Response:
        raise NotImplementedError("TODO")


class LikedSpecificLikeView(views.APIView):
    """
    - URL:`://service/api/liked/{LIKE_FQID}`
        - `GET`[local] a single like
        - Body is [like object]
    """
    @extend_schema(
        description="Get a single like by FQID",
        responses=serializers.LikeSerializer,
        parameters=[
            OpenApiParameter("like_fqid", str, OpenApiParameter.PATH,
                             description="FQID of the like in question"),
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, like_fqid: str) -> Response:
        raise NotImplementedError("TODO")
