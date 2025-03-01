from typing import Optional

from itertools import chain

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


# Author related views

class AuthorsView(views.APIView):
    """Author list API view"""

    @extend_schema(
        summary="Get authors",
        description="Get a list of authors",
        responses=serializers.AuthorsSerializer
    )
    @method_decorator(user_controller())
    def get(self, request: Request) -> Response:
        """Get authors API view"""
        local_authors = models.LocalAuthor.objects.all()
        remote_authors = models.RemoteAuthor.objects.all()
        authors = sorted(chain(local_authors, remote_authors),
                         key=lambda x: x.username)
        serializer = serializers.AuthorsSerializer(authors)
        return Response(serializer.data)


class AuthorView(views.APIView):
    """Author API view"""

    @extend_schema(
        summary="Get author",
        description="Get an author by their UUID",
        responses=serializers.AuthorSerializer,
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: Optional[str] = None) -> Response:
        """Get author API view"""
        author = get_object_or_404(models.Author, uuid=author_uuid)
        serializer = serializers.AuthorSerializer(author)
        return Response(serializer.data)

    @extend_schema(
        summary="Update author",
        description="Update an author by their UUID",
        responses=serializers.AuthorSerializer,
    )
    @method_decorator(user_controller())
    def put(self, request: Request, author_uuid: Optional[str] = None, viewer: Optional[models.LocalAuthor] = None) -> Response:

        viewer_is_superuser = request.user.is_superuser
        viewer_is_author = getattr(viewer, "uuid", None) == author_uuid
        user_control(request,
                     verify_true=(viewer_is_superuser or viewer_is_author))
        serializer = serializers.AuthorSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User updated successfully",
                             "author": serializer.data})
        else:
            return Response({"error": "Error saving author",
                             "author": serializer.errors})
