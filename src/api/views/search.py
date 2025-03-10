from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.db.models import Q
from socialnetwork.models import LocalAuthor
from socialnetwork.serializers import LocalAuthorSerializer
from typing import Any

class AuthorSearchView(APIView):
    """
    GET /api/search/authors/?q=...
    Returns a list of LocalAuthors whose username contains the query.
    """
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        query: str = request.GET.get("q", "").strip()
        print(f"Searching for authors with username: '{query}'")

        if query:
            authors = LocalAuthor.objects.filter(user__username__icontains=query)
        else:
            authors = LocalAuthor.objects.none()

        serializer = LocalAuthorSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
