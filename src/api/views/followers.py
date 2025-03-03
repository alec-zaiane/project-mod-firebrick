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

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str) -> Response:
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

    )
    @method_decorator(user_controller())
    def delete(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def put(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, foreign_author_fqid: str) -> Response:
        raise NotImplementedError("TODO")
