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
from socialnetwork.utils.uuid_validator import check_uuid_valid
from socialnetwork import models
from api import serializers


class AuthorsView(views.APIView):
    """Author list API view

    Example from class page:
    - URL: `://service/api/authors/`
        - GET [local, remote]: retrieve all profiles on the node (paginated)
            - page: how many pages
            - size: how big is a page
    - Example query: `GET ://service/api/authors?page=10&size=5`
        - Gets the 5 authors, authors 45 to 49.
    """

    @extend_schema(
        summary="Get authors",
        description="Get a list of authors (paginated, default 50 authors per page)",
        responses=serializers.AuthorsSerializer,
        parameters=[
            OpenApiParameter("page", type=int,
                             description="Page number to fetch (1-indexed)", default=1),
            OpenApiParameter("size", type=int,
                             description="How many authors per page", default=50)
        ]
    )
    @method_decorator(user_controller())
    def get(self, request: Request) -> Response:
        """Get authors API view"""
        try:
            paginate_page = int(request.query_params.get("page", 1))
            paginate_size = int(request.query_params.get("size", 50))
        except ValueError:
            return Response("Incorrectly formatted `page` or `size` parameter", 400)

        index_start = (paginate_page-1)*paginate_size
        local_authors = models.LocalAuthor.objects.all()
        remote_authors = models.RemoteAuthor.objects.all()
        authors = sorted(chain(local_authors, remote_authors),
                         key=lambda x: x.username)[index_start:index_start+paginate_size]
        serializer = serializers.AuthorsSerializer(authors)
        return Response(serializer.data)


class AuthorView(views.APIView):
    """Author API view

    Details from class page:
    - URL: `://service/api/authors/{AUTHOR_SERIAL}/`
        - GET [local, remote]: retrieve AUTHOR_SERIAL's profile
        - PUT [local]: update AUTHOR_SERIAL's profile
    - URL: `://service/api/authors/{AUTHOR_FQID}/`
        - GET [local]: retrieve AUTHOR_FQID's profile
    TODO get GET working with FQIDs as well
    """

    @extend_schema(
        summary="Get author",
        description="Get an author by their UUID",
        responses=serializers.AuthorSerializer,
    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid_or_fqid: str) -> Response:
        """Get author API view"""
        author = None
        if check_uuid_valid(author_uuid_or_fqid):
            author = get_object_or_404(models.Author, uuid=author_uuid_or_fqid)
        else:
            author = models.Author.get_author_by_FQID(author_uuid_or_fqid)
        serializer = serializers.AuthorSerializer(author)
        return Response(serializer.data)

    @extend_schema(
        summary="Update author",
        description="Update an author by their UUID",
        request=serializers.AuthorSerializer,
        responses=serializers.AuthorSerializer,
    )
    @method_decorator(user_controller())
    def put(self, request: Request, author_uuid_or_fqid: Optional[str] = None, viewer: Optional[models.LocalAuthor] = None) -> Response:
        viewer_is_superuser = request.user.is_superuser
        viewer_is_author = getattr(viewer, "uuid", None) == author_uuid_or_fqid
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
