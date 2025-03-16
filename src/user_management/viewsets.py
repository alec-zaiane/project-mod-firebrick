from typing import Any

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from user_management.models import Author, Node
from user_management.serializers import AuthorSerializer

from user_management.permissions import AuthorPermission


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AuthorPermission]

    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]  # fix for pagination
        return Response({
            "type": "authors",
            "items": super_data
        })

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict[str, Any] = serializer.validated_data
        # make sure we cannot create authors on this node (if you want to create an author on this node, use the join request system)
        if validated_data["host__host_url"] == Node.objects.get_local_node().host_url:
            return Response("Cannot create authors on this node", status=400)
        # Make sure we can only create authors that are not already in the database
        if Author.objects.filter(fqid=validated_data["fqid"]).exists():
            return Response("Author already exists", status=400)
        # check if the author exists on a node we don't have
        host = Node.external_nodes.find_node(validated_data.pop("host__host_url"))
        if host is None:
            return Response("Host does not exist", status=400)
        validated_data["host_node"] = host
        # create the author
        author = serializer.create(validated_data)
        return Response(serializer.to_representation(author), status=201)
