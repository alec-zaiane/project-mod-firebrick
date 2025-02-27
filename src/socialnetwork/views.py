from typing import Optional

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.urls import reverse

from socialnetwork.utils.user_control_decorator import user_control
from . import models


# General Views
# This file is for views that show browser output (eg: render a template), use views_api.py for rest_framework API views

def get_unauthenticated_response() -> HttpResponse:
    return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))


def not_logged_in_view(request: HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")


@user_control(must_be_logged_in=True, must_be_author=True)
def stream_view(request: HttpRequest, viewer: Optional[models.LocalAuthor]) -> HttpResponse:
    """An author's stream view"""
    if viewer is None:  # shouldn't be possible, needed for mypy
        return get_unauthenticated_response()

    page = int(request.GET.get('page', '1'))
    size = int(request.GET.get('size', '10'))
    start = (page - 1) * size

    posts = viewer.get_stream(paginate_start=start, paginate_count=size)

    return render(request, "stream.html", {
        "user": request.user,
        "viewer": viewer,
        "posts": posts,
        "current_page": page,
    })


@user_control(must_be_logged_in=True, must_be_author=True)
def author_profile_view(request: HttpRequest, target_author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""

    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    author_posts = models.PostTextBased.objects.filter(
        base_author=target_author, is_deleted=False)
    author_posts_sorted = sorted(
        author_posts, key=lambda x: x.date_created, reverse=True
    )

    return render(request, "author_profile.html", {"author": target_author, "viewer": viewer, "posts": author_posts_sorted})


@user_control(must_be_logged_in=True, must_be_author=True)
def local_author_modify_view(request: HttpRequest, target_author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """Modify `target_author_uuid`'s profile"""
    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    if viewer != target_author and not request.user.is_superuser:
        return HttpResponse("You do not have permission to modify this author", status=403)
    return render(request, "local_author_modify.html", {"author": target_author, "viewer": viewer})

# Views for Posts


@user_control(must_be_logged_in=True, must_be_author=True)
def create_post_view(request: HttpRequest, viewer: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to create a post."""
    return render(request, "create_post.html", {"author": viewer})


@user_control(must_be_logged_in=True, must_be_author=True)
def edit_post_view(request: HttpRequest, post_uuid: str, viewer: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to edit their post and toggle between Plain Text and Markdown."""

    post = get_object_or_404(models.PostTextBased, uuid=post_uuid)

    # only the author of the post can edit
    if post.author != viewer:
        return HttpResponse("You do not have permission to edit this post.", status=403)

    return render(request, "edit_post.html", {"post": post, "author": viewer})
