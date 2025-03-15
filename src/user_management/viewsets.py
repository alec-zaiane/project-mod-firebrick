from rest_framework import viewsets

from user_management.models import Author
from user_management.serializers import AuthorSerializer


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
