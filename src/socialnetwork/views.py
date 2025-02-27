from typing import Optional

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.urls import reverse

from socialnetwork.utils.user_control_decorator import user_control
from . import models


# General Views
# This file is for views that show browser output (eg: render a template), use views_api.py for rest_framework API views

def not_logged_in_view(request: HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")


@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=True, superuser_requires_author=True)
def stream_view(request: HttpRequest, author: models.LocalAuthor) -> HttpResponse:
    """An author's stream view"""
    page = int(request.GET.get('page', '1'))
    size = int(request.GET.get('size', '10'))
    start = (page - 1) * size

    posts = author.get_stream(paginate_start=start, paginate_count=size)

    return render(request, "stream.html", {
        "user": request.user,
        "viewer": author,
        "posts": posts,
        "current_page": page,
    })


@user_control(can_be_author=True, can_be_logged_out=True, can_be_superuser=True)
def author_profile_view(request: HttpRequest, target_author_uuid: str, author: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""

    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    author_posts = models.PostTextBased.objects.filter(
        base_author=target_author, is_deleted=False)
    author_posts_sorted = sorted(
        author_posts, key=lambda x: x.date_created, reverse=True)

    return render(request, "author_profile.html", {"author": target_author, "viewer": author, "posts": author_posts_sorted})


@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=True)
def local_author_modify_view(request: HttpRequest, target_author_uuid: str, author: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """Modify `target_author_uuid`'s profile"""
    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    if author != target_author and not request.user.is_superuser:
        return HttpResponse("You do not have permission to modify this author", status=403)
    return render(request, "local_author_modify.html", {"author": target_author, "viewer": author})

# Views for Posts


@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def create_post_view(request: HttpRequest, author: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to create a post."""
    return render(request, "create_post.html", {"author": author})


@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def edit_post_view(request: HttpRequest, post_uuid: str, author: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to edit their post and toggle between Plain Text and Markdown."""

    post = get_object_or_404(models.PostTextBased, uuid=post_uuid)

    # only the author of the post can edit
    if post.author != author:
        return HttpResponse("You do not have permission to edit this post.", status=403)

    if request.method == "POST":
        new_content = request.POST.get("content")
        new_post_type = request.POST.get("post_type")

        if new_content and new_post_type in [models.PostTextBased.TextPostTypes.PLAINTEXT, models.PostTextBased.TextPostTypes.MARKDOWN]:
            post.content = new_content
            post.post_type = new_post_type
            post._finalize_edit()
            return redirect("socialnetwork:stream")

    return render(request, "edit_post.html", {"post": post, "author": author})
