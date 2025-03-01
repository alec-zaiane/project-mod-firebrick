from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema

from socialnetwork.utils.user_control_decorator import user_controller, user_control
from socialnetwork import models
from api import serializers


# This file is for only API views, standardized to our API spec
# see https://uofa-cmput404.github.io/general/project.html#api-endpoints

class AuthorView(views.APIView):
    """Author API view"""

    @extend_schema(
        summary="Get author",
        description="Get an author by their UUID",
        responses=serializers.AuthorSerializer
    )
    @method_decorator(user_controller(must_be_logged_in=True))
    def get(self, request: Request, author_uuid: Optional[str] = None) -> Response:
        """Get author API view"""
        author = get_object_or_404(models.Author, uuid=author_uuid)
        serializer = serializers.AuthorSerializer(author)
        return Response(serializer.data)
