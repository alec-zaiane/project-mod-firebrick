from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db.models import Q

from typing import Any
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user_management.models import Author, FollowRequest
from user_management.serializers import AuthorSerializer, FollowRequestSerializer

from django.urls import reverse

from django.template import loader

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from user_management.forms import AuthorModifyForm, JoinRequestForm
from user_management.models import LocalAuthor
from core.utils.request_viewer import get_request_viewer
from posts.models import Post, VisibilityTypes

# ========= Frontend Views only! =========


class JoinView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        The view for making a join request. It provides a form to submit a join request to the admins.
        """
        form = JoinRequestForm()
        return render(request, "registration/join.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        When posting the join request, it will attempt to validate the form, and then save the join
        request. The form will automatically set a default display_name equal to the username.
        On success, it will render the join_success.html template, but not change the url.
        """
        form = JoinRequestForm(request.POST)
        viewer = get_request_viewer(request)
        if viewer is not None and not viewer.user.is_superuser:
            # If the user is already logged in, they should not be able to make a join request (unless they are an admin)
            return HttpResponseRedirect(reverse("posts:stream"))
        if form.is_valid():
            form.save()
            return render(request, "registration/join_success.html")
        return render(request, "registration/join.html", {"form": form})


class AuthorView(View):
    def get(self, request: HttpRequest, target_author_uuid: str) -> HttpResponse:
        """
        The view for viewing an author's profile. It can be linked to from any author's
        UUID, and will display information about the author.
        """
        try:
            target_author = Author.objects.get(uuid=target_author_uuid)
        except Author.DoesNotExist:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        if target_author.host_node.is_disabled:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        viewer = get_request_viewer(request)

        public_posts = Post.visible_posts.filter(
            author=target_author, visibility_type=VisibilityTypes.PUBLIC
        ).order_by("-created_at")

        is_following = target_author in viewer.following.all() if viewer is not None else False
        is_follow_requested = viewer.follow_requests_sent.filter(
            followee=target_author).exists() if viewer is not None else False

        following = target_author.following.all()
        followers = target_author.followers.all()
        friends = target_author.friends.all()

        return render(
            request,
            "author_profile.html",
            {
                "author": target_author,
                "viewer": viewer,
                "posts": public_posts,
                "is_following": is_following,
                "is_follow_requested": is_follow_requested,
                "following": following,
                "followers": followers,
                "friends": friends
            },
        )


class AuthorModifyView(View):
    def get(self, request: HttpRequest, target_author_uuid: str) -> HttpResponse:
        """
        The view for modifying an author's profile. It can be linked to from any author's
        UUID, and will allow the viewer, if valid, to modify the author's profile.
        """
        try:
            target_author = Author.objects.get(uuid=target_author_uuid)
        except Author.DoesNotExist:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        if target_author.host_node.is_disabled:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        viewer = get_request_viewer(request)
        if viewer is None or (viewer != target_author and not viewer.user.is_superuser):
            # Send the user back to the author's profile if they are not the author or an admin
            return render(request, "author_profile.html", {
                "author": target_author,
            })

        form = AuthorModifyForm(instance=target_author)
        return render(request, "author_modify.html", {
            "author": target_author,
            "form": form
        })

    def post(self, request: HttpRequest, target_author_uuid: str) -> HttpResponse:
        """
        The view for modifying an author's profile. It can be linked to from any author's
        UUID, and will display information about the author.
        """
        try:
            target_author = Author.objects.get(uuid=target_author_uuid)
        except Author.DoesNotExist:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        if target_author.host_node.is_disabled:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        viewer = get_request_viewer(request)
        if viewer is None or (viewer != target_author and not viewer.user.is_superuser):
            # Send the user back to the author's profile if they are not the author or an admin
            return render(request, "author_profile.html", {
                "author": target_author,
            })

        form = AuthorModifyForm(request.POST, instance=target_author)
        if form.is_valid():
            form.save()
            return render(request, "author_modify_success.html", {
                "author": target_author,
                "form": form
            })
        return render(request, "author_modify.html", {
            "author": target_author,
            "form": form
        })


class AuthorFollowRequests(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        The view for viewing all of the follow requests that belong to an author.
        """

        viewer = get_request_viewer(request)

        if viewer == None:
            if request.GET.get('next') == None:
                return HttpResponseRedirect(reverse("user_management:login") + "?next=" + reverse("user_management:follow_requests"))
            return HttpResponseRedirect(reverse("user_management:login") + "?next=" + reverse("user_management:follow_requests") + "?next=" + request.GET.get('next', ''))

        follow_requests = viewer.follow_requests_received.all()

        return render(
            request,
            "follow_requests.html",
            {
                "author": viewer,
                "viewer": viewer,
                "follow_requests": follow_requests
            },
        )


class AuthorFollowInfoView(View):
    follow_type: str = ""

    def get(self, request: HttpRequest, target_author_uuid: str) -> HttpResponse:
        """
        The view for viewing all of the follow info that belongs to an author.
        Represents all three main types, since they all use the same template and are otherwise extremely similar.
        That is: following, followers, and friends.
        """

        try:
            target_author = Author.objects.get(uuid=target_author_uuid)
        except Author.DoesNotExist:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        if target_author.host_node.is_disabled:
            return render(request, "author_not_found.html", {
                "error_uuid": target_author_uuid,
            })

        viewer = get_request_viewer(request)

        if viewer == None:
            if request.GET.get('next') == None:
                return HttpResponseRedirect(reverse("user_management:login") + "?next=" + reverse("user_management:author_following", args=[target_author.uuid]))
            return HttpResponseRedirect(reverse("user_management:login") + "?next=" + reverse("user_management:author_following", args=[target_author.uuid]) + "?next=" + request.GET.get('next', ''))

        if self.follow_type == "following":
            follow_info = target_author.following.all()
        elif self.follow_type == "followers":
            follow_info = target_author.followers.all()
        elif self.follow_type == "friends":
            follow_info = target_author.friends.all()
        else:
            return HttpResponse(status=404)

        return render(
            request,
            "follow_info.html",
            {
                "author": target_author,
                "viewer": viewer,
                "follow_info": follow_info,
                "follow_type": self.follow_type.capitalize()
            },
        )


class AuthorSearchAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Search Authors",
        description="Search for authors by their username or display name. Returns matching authors.",
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search query string to match against usernames and display names",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AuthorSerializer(many=True),
                description="List of matching authors",
            ),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Authentication credentials were not provided.",
                        }
                    },
                },
            ),
        },
        tags=["Authors"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        query = request.query_params.get("q", "")
        authors = Author.objects.filter(
            Q(username__icontains=query) | Q(
                display_name__icontains=query) & Q(host_node__is_disabled=False)
        )
        authors_list: list[dict[str, str]] = []
        # Necessary instead of serializer, because we need UUID
        for author in authors:
            author_data: dict[str, str] = {
                "displayName": str(author.display_name),
                "username": str(author.username),
                "profileImage": str(author.profile_image),
                "uuid": str(author.uuid),
                "host_url": str(author.host_node.host_url),
            }
            authors_list.append(author_data)
        return Response(authors_list)


class FollowRequestByViewer(APIView):

    @extend_schema(
        operation_id="create_follow_request_by_viewer",
        summary="[Internal] Create follow request",
        description="Create a follow request for an author by the authenticated viewer. Cannot create duplicate requests or request to follow already-followed authors.",
        parameters=[
            OpenApiParameter(
                name="target_fqid",
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author to follow",
                required=True,
                type=str,
            ),
        ],
        responses={
            201: OpenApiResponse(
                description="Follow request created successfully",
            ),
            400: OpenApiResponse(
                description="Invalid request",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "You are already following this author",
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
                            "example": "Log in as a user to follow an author",
                        }
                    },
                },
            ),
            404: OpenApiResponse(
                description="Author not found",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Could not find author with id {target_fqid}",
                        }
                    },
                },
            ),
        },
        tags=["Follow Requests"],
    )
    def post(self, request: Request, target_fqid: str) -> Response:
        """Create a follow request for an author by the viewer.
        Cannot create a follow request for an author that has already been followed by the viewer.
        """
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response({"error": "Log in as a user to follow an author"}, status=401)

        target_author = Author.objects.find_by_encoded_fqid(target_fqid)
        if target_author is None:
            return Response({"error": f"Could not find author with id {target_fqid}"}, status=404)
        if viewer.following.filter(fqid=target_fqid).exists():
            return Response({"error": "You are already following this author"}, status=400)
        if viewer.follow_requests_sent.filter(followee=target_author).exists():
            return Response({"error": "You have already requested to follow this author"}, status=400)
        # deserialize and validate the incoming follow request data
        FollowRequest.objects.create_follow_request(viewer, target_author)
        return Response(status=201)

    @extend_schema(
        operation_id="delete_follow_request_by_viewer",
        summary="[Internal] Delete follow request",
        description="Delete a follow request created by the authenticated viewer. Can only delete requests that exist and were created by the viewer.",
        parameters=[
            OpenApiParameter(
                name="target_fqid",
                location=OpenApiParameter.PATH,
                description="The fully qualified ID of the author whose follow request to delete",
                required=True,
                type=str,
            ),
        ],
        responses={
            204: OpenApiResponse(description="Follow request deleted successfully"),
            401: OpenApiResponse(
                description="Authentication required",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Log in as a user to remove a follow request from an author",
                        }
                    },
                },
            ),
            404: OpenApiResponse(
                description="Follow request not found",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "You have not requested to follow this author",
                        }
                    },
                },
            ),
        },
        tags=["Follow Requests"],
    )
    def delete(self, request: Request, target_fqid: str) -> Response:
        """Delete a follow request for an author by the viewer.
        Cannot delete a follow request for an author that has not been requested to be followed by the viewer.
        """
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response({"error": "Log in as a user to remove a follow request from an author"}, status=401)

        target_author = Author.objects.find_by_encoded_fqid(target_fqid)
        if target_author is None:
            return Response({"error": f"Could not find author with id {target_fqid}"}, status=404)
        if not viewer.follow_requests_sent.filter(followee=target_author).exists():
            return Response({"error": "You have not requested to follow this author"}, status=404)
        viewer.follow_requests_sent.filter(followee=target_author).delete()
        return Response(status=204)
