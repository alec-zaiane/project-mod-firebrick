from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer
from user_management.models import Author, FollowRequest
from typing import Any

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from user_management.models import Author, Node, FollowRequest
from user_management.serializers import AuthorSerializer, FollowRequestSerializer

from user_management.permissions import AuthorPermission
from core.utils.request_viewer import get_request_viewer

from urllib.parse import unquote


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded fqid
    lookup_field = "fqid"
    lookup_url_kwarg = "fqid"
    lookup_value_regex = ".+"
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, AuthorPermission]

    def get_object(self) -> Author:
        """Allow for encoded fqid based lookup"""
        fqid = self.kwargs.get("fqid", None)
        if fqid is not None:
            lookup_field = "fqid"
            lookup_value = unquote(fqid)
            return self.get_queryset().get(**{lookup_field: lookup_value})
        return super().get_object()

    @extend_schema(
        summary="List all authors",
        description="Get a paginated list of all authors in the system.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                description="Page number for pagination",
                required=False,
            ),
            OpenApiParameter(
                name="size",
                type=int,
                description="Number of items per page",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="List of authors retrieved successfully",
                response={
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "example": "authors"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Author"},
                        },
                    },
                },
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Authors"],
    )
    def list(self, request: Request) -> Response:
        super_data = super().list(request).data
        if super_data.get("results", None) is not None:
            super_data = super_data["results"]  # fix for pagination
        return Response({
            "type": "authors",
            "items": super_data
        })

    @extend_schema(
        summary="Create external author",
        description="Create a new external author. Local authors must be created through the join system.",
        request=AuthorSerializer,
        responses={
            201: OpenApiResponse(
                response=AuthorSerializer, description="Author created successfully"
            ),
            400: OpenApiResponse(
                description="Bad request",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Cannot create authors on this node",
                        }
                    },
                },
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Authors"],
    )
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

    @extend_schema(
        summary="Get author details",
        description="Get details of a specific author using their fully qualified ID (FQID)",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author",
            )
        ],
        responses={
            200: AuthorSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Authors"],
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update author (Full)",
        description="Fully update an author's information. All fields must be provided.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author",
            )
        ],
        request=AuthorSerializer,
        responses={
            200: AuthorSerializer,
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this author"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Authors"],
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Update author (Partial)",
        description="Partially update an author's information. Only provided fields will be updated.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author",
            )
        ],
        request=AuthorSerializer,
        responses={
            200: AuthorSerializer,
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this author"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Authors"],
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete author",
        description="Delete an author. Only administrators can delete authors.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author",
            )
        ],
        responses={
            204: OpenApiResponse(description="Author successfully deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to delete this author"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Authors"],
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Unfollow an author",
        description="Remove a following relationship with the specified author",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author to unfollow",
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Successfully unfollowed author",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Unfollowed successfully.",
                        }
                    },
                },
            ),
            400: OpenApiResponse(description="Not following this author"),
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Authors"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="unfollow",
        url_name="unfollow",
        permission_classes=[IsAuthenticated],
    )
    def unfollow(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        viewer = get_request_viewer(request)
        if request.user.is_anonymous or viewer is None:
            return Response(
                {"error": "User must be authenticated and linked to an author."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        target_author = self.get_object()
        if target_author not in viewer.following.all():
            return Response(
                {"error": "You are not following this author."},
                status=status.HTTP_400_BAD_REQUEST
            )
        viewer.following.remove(target_author)
        return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_200_OK)

class FollowRequestViewSet(viewsets.ModelViewSet[FollowRequest]):
    # suggested by copilot: lookup_field/lookup_url_kwarg/lookup_value_regex to change the lookup field to an encoded fqid
    lookup_field = "fqid"
    lookup_url_kwarg = "fqid"
    lookup_value_regex = ".+"
    queryset = FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> FollowRequest:
        """Allow for encoded fqid based lookup"""
        fqid = self.kwargs.get("fqid", None)
        if fqid is not None:
            lookup_field = "fqid"
            lookup_value = unquote(fqid)
            return self.get_queryset().get(**{lookup_field: lookup_value})
        return super().get_object()

    @extend_schema(
        summary="List follow requests",
        description="Get a list of all follow requests. Results are paginated.",
        responses={
            200: FollowRequestSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Follow Requests"],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create follow request",
        description="Send a new follow request to another author.",
        request=FollowRequestSerializer,
        responses={
            201: FollowRequestSerializer,
            400: OpenApiResponse(description="Invalid follow request data"),
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Target author not found"),
            409: OpenApiResponse(description="Already following or request exists"),
        },
        tags=["Follow Requests"],
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        viewer = get_request_viewer(request)
        if request.user.is_anonymous or viewer is None:
            return Response({"error": "User must be authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        # deserialize and validate the incoming follow request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # check that the actor in the request matches the logged-in user
        input_actor = request.data.get("actor", {})
        if input_actor.get("id") and viewer.fqid != input_actor["id"]:
            return Response({"error": "Logged in user does not match actor in request."}, status=status.HTTP_403_FORBIDDEN)

        follow_request = serializer.save()
        return Response(self.get_serializer(follow_request).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get follow request details",
        description="Get details of a specific follow request by its FQID.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request"
            )
        ],
        responses={
            200: FollowRequestSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Follow request not found")
        },
        tags=["Follow Requests"]
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update follow request (Full)",
        description="Fully update a follow request. All fields must be provided.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request"
            )
        ],
        request=FollowRequestSerializer,
        responses={
            200: FollowRequestSerializer,
            400: OpenApiResponse(description="Invalid follow request data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this request"),
            404: OpenApiResponse(description="Follow request not found")
        },
        tags=["Follow Requests"]
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Update follow request (Partial)",
        description="Partially update a follow request. Only provided fields will be updated.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request"
            )
        ],
        request=FollowRequestSerializer,
        responses={
            200: FollowRequestSerializer,
            400: OpenApiResponse(description="Invalid follow request data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to update this request"),
            404: OpenApiResponse(description="Follow request not found")
        },
        tags=["Follow Requests"]
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete follow request",
        description="Delete a follow request. Only the sender or recipient can delete it.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request"
            )
        ],
        responses={
            204: OpenApiResponse(description="Follow request deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to delete this request"),
            404: OpenApiResponse(description="Follow request not found")
        },
        tags=["Follow Requests"]
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        operation_id="follow_request_approve",
        summary="Approve follow request",
        description="Approve a follow request. Only the recipient (followee) can approve it.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request",
                required=True,
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Follow request approved successfully",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Follow request approved.",
                        }
                    },
                },
            ),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "User must be authenticated and linked to an author.",
                        }
                    },
                },
            ),
            403: OpenApiResponse(
                description="Not authorized",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "You do not have permission to approve this follow request.",
                        }
                    },
                },
            ),
            404: OpenApiResponse(description="Follow request not found"),
        },
        tags=["Follow Requests"],
    )
    @action(detail=True, methods=["post"], url_path="approve", url_name="approve")
    def approve_follow_request(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # ensure user is authenticated and has an associated author
        if request.user.is_anonymous or not hasattr(request.user, "author"):
            return Response({"error": "User must be authenticated and linked to an author."},
                            status=status.HTTP_401_UNAUTHORIZED)
        logged_in_author = request.user.author

        follow_request = self.get_object()
        # only the followee should be allowed to approve the request
        if logged_in_author != follow_request.followee:
            return Response(
                {"error": "You do not have permission to approve this follow request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # approve by adding the follow relationship and deleting the request
        follow_request.follower.following.add(follow_request.followee)
        follow_request.delete()
        return Response({"detail": "Follow request approved."}, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="follow_request_deny",
        summary="Deny follow request",
        description="Deny a follow request. Only the recipient (followee) can deny it.",
        parameters=[
            OpenApiParameter(
                name="fqid",
                type=str,
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the follow request",
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Follow request denied successfully",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Follow request denied."
                        }
                    }
                }
            ),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "User must be authenticated and linked to an author."
                        }
                    }
                }
            ),
            403: OpenApiResponse(
                description="Not authorized",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "You do not have permission to deny this follow request."
                        }
                    }
                }
            ),
            404: OpenApiResponse(description="Follow request not found")
        },
        tags=["Follow Requests"]
    )
    @action(detail=True, methods=["post"], url_path="deny", url_name="deny")
    def deny_follow_request(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if request.user.is_anonymous or not hasattr(request.user, "author"):
            return Response({"error": "User must be authenticated and linked to an author."},
                            status=status.HTTP_401_UNAUTHORIZED)
        logged_in_author = request.user.author

        follow_request = self.get_object()
        if logged_in_author != follow_request.followee:
            return Response(
                {"error": "You do not have permission to deny this follow request."},
                status=status.HTTP_403_FORBIDDEN
            )
        follow_request.delete()
        return Response({"detail": "Follow request denied."}, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="follow_request_pending_count",
        summary="Get pending follow request count",
        description="Get the number of pending follow requests for the authenticated user.",
        responses={
            200: OpenApiResponse(
                description="Count retrieved successfully",
                response={
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "Number of pending follow requests",
                            "example": 5,
                        }
                    },
                },
            )
        },
        tags=["Follow Requests"],
    )
    def pending_count(self, request: Request) -> Response:
        viewer = get_request_viewer(request)
        if not viewer:
            # not logged in or not linked to an Author will return 0
            return Response({"count": 0}, status=status.HTTP_200_OK)

        # all FollowRequest rows that have the viewer as the followee are pending
        count = FollowRequest.objects.filter(followee=viewer).count()
        return Response({"count": count}, status=status.HTTP_200_OK)
