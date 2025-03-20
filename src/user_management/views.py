from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

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

        return render(
            request,
            "author_profile.html",
            {
                "author": target_author,
                "viewer": viewer,
                "posts": public_posts,
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
