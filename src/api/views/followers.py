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


# ============== Followers =============
"""Followers API view

Details from class page:
- URL: `://service/api/authors/{AUTHOR_SERIAL}/followers`
    - GET [local, remote]: get a list of authors who are AUTHOR_SERIAL's followers
- URL: `://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID}`
    - Note: foreign author ID should be a percent encoded URL of the foreign author. An example URL would be: `http://example-node-1/api/authors/178aba49-ca39-4741-b227-f40d072b1222/followers/http%3A%2F%2Fexample-node-2%2Fauthors%2F5f57808f-0bc9-4b3d-bdd1-bb07c976d12d`
    - DELETE [local]: remove FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
    - PUT [local]: Add FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
    - GET [local, remote] check if FOREIGN_AUTHOR_FQID is a follower of AUTHOR_SERIAL
        - Should return 404 if they're not
        - This is how you can check if follow request is accepted
"""


class FollowersView(views.APIView):
    """
    - URL: `://service/api/authors/{AUTHOR_SERIAL}/followers`
        - GET [local, remote]: get a list of authors who are AUTHOR_SERIAL's followers
    """

    @extend_schema(
        description="Get a list of authors who are following a specific author",
        responses=serializers.AuthorsSerializer,
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author"),
            OpenApiParameter("page", type=int,
                             description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter("size", type=int,
                             description="How many authors per page", default=50),
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str) -> Response:
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)
        raise NotImplementedError("TODO")


class FollowersSpecificView(views.APIView):
    """
    - URL: `://service/api/authors/{AUTHOR_SERIAL}/followers/{FOREIGN_AUTHOR_FQID}`
        - Note: foreign author ID should be a percent encoded URL of the foreign author. An example URL would be: `http://example-node-1/api/authors/178aba49-ca39-4741-b227-f40d072b1222/followers/http%3A%2F%2Fexample-node-2%2Fauthors%2F5f57808f-0bc9-4b3d-bdd1-bb07c976d12d`
        - DELETE [local]: remove FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
        - PUT [local]: Add FOREIGN_AUTHOR_FQID as a follower of AUTHOR_SERIAL (must be authenticated)
        - GET [local, remote] check if FOREIGN_AUTHOR_FQID is a follower of AUTHOR_SERIAL
            - Should return 404 if they're not
            - This is how you can check if follow request is accepted
    """
    @extend_schema(
        description="Remove a follower from an author",
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author to remove the follower from"),
            OpenApiParameter("foreign_author_fqid", type=str, location=OpenApiParameter.PATH,
                             description="The FQID of the author to remove as a follower"),
        ],
        # responses= TODO
    )
    @method_decorator(user_controller())
    def delete(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(
        description="Add a follower to an author (must be authenticated)",
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author to add the follower to"),
            OpenApiParameter("foreign_author_fqid", type=str, location=OpenApiParameter.PATH,
                             description="The FQID of the author to add as a follower"),
        ],
        # responses= TODO
    )
    @method_decorator(user_controller())
    def put(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(
        description="Check if a follower is following an author",
        parameters=[
            OpenApiParameter("author_uuid", type=str, location=OpenApiParameter.PATH,
                             description="The UUID of the author to check the follower status of"),
            OpenApiParameter("foreign_author_fqid", type=str, location=OpenApiParameter.PATH,
                             description="The FQID of the author to check if they are a follower"),
        ],
        # responses= TODO 404 if not a follower
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")
