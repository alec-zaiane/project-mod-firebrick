from typing import Any

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from user_management.models import Author, Node, FollowRequest
from user_management.serializers import AuthorSerializer, FollowRequestSerializer

from user_management.permissions import AuthorPermission


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, AuthorPermission]

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


class FollowRequestViewSet(viewsets.ModelViewSet[FollowRequest]):
    queryset = FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if request.user.is_anonymous:
            return Response({"error": "User must be authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        logged_in_author = request.user.author
        # deserialize and validate the incoming follow request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # check that the actor in the request matches the logged-in user
        input_actor = request.data.get("actor", {})
        if input_actor.get("id") and logged_in_author.fqid != input_actor["id"]:
            return Response({"error": "Logged in user does not match actor in request."}, status=status.HTTP_403_FORBIDDEN)

        follow_request = serializer.save()
        return Response(self.get_serializer(follow_request).data, status=status.HTTP_201_CREATED)
