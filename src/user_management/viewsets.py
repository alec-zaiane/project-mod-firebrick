from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from user_management.models import Author
from user_management.serializers import AuthorSerializer


class AuthorViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        raise NotImplementedError()

    def create(self, request: Request) -> Response:
        raise NotImplementedError()

    def retrieve(self, request: Request, pk: int) -> Response:
        raise NotImplementedError()

    def update(self, request: Request, pk: int) -> Response:
        raise NotImplementedError()

    def partial_update(self, request: Request, pk: int) -> Response:
        raise NotImplementedError()

    def destroy(self, request: Request, pk: int) -> Response:
        raise NotImplementedError()
