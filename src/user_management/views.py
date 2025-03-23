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

from drf_spectacular.utils import extend_schema

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
        target_author = get_object_or_404(
            LocalAuthor, uuid=target_author_uuid)

        viewer = get_request_viewer(request)

        public_posts = Post.visible_posts.filter(
            author=target_author, visibility_type=VisibilityTypes.PUBLIC
        ).order_by("-created_at")

        is_following = target_author in viewer.following.all() if viewer is not None else False
        is_follow_requested = viewer.follow_requests_sent.filter(
            followee=target_author).exists() if viewer is not None else False

        return render(
            request,
            "author_profile.html",
            {
                "author": target_author,
                "viewer": viewer,
                "posts": public_posts,
                "is_following": is_following,
                "is_follow_requested": is_follow_requested
            },
        )


class AuthorModifyView(View):
    def get(self, request: HttpRequest, target_author_uuid: str) -> HttpResponse:
        """
        The view for modifying an author's profile. It can be linked to from any author's
        UUID, and will allow the viewer, if valid, to modify the author's profile.
        """
        target_author = get_object_or_404(
            LocalAuthor, uuid=target_author_uuid)

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
        target_author = get_object_or_404(
            LocalAuthor, uuid=target_author_uuid)

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


class AuthorSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        query = request.query_params.get("q", "")
        authors = Author.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        )
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)


class FollowRequestByViewer(APIView):
    @extend_schema(
        summary="[Internal] create a follow request for an author by the viewer",
        description="Create a follow request for an author by the viewer. Cannot create a follow request for an author that has already been followed by the viewer.",
        responses={201: None, 400: None, 401: None, 404: None},
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
