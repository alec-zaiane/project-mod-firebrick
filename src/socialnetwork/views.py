from typing import Optional

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django.urls import reverse

from socialnetwork.utils.user_control_decorator import user_controller
from . import models
from socialnetwork.models import FollowRequest

from django.http import JsonResponse
from django.db.models import Q
from .models import LocalAuthor
from django.contrib.auth.models import AnonymousUser

from itertools import chain

# General Views
# This file is for views that show browser output (eg: render a template), use views_api.py for rest_framework API views

def get_unauthenticated_response() -> HttpResponse:
    return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))


def not_logged_in_view(request: HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:stream"))
    return render(request, "registration/not_logged_in.html")


@user_controller(must_be_logged_in=True, must_be_author=True)
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


@user_controller(must_be_logged_in=True, must_be_author=True)
def author_profile_view(request: HttpRequest, target_author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""
    target_author = get_object_or_404(models.LocalAuthor, uuid=target_author_uuid)
    
    # Retrieve text-based posts
    text_posts = models.PostTextBased.objects.filter(
        base_author=target_author, is_deleted=False)
    
    # Retrieve media-based (image) posts
    media_posts = models.PostMediaBased.objects.filter(
        base_author=target_author, is_deleted=False)
    
    # Combine both querysets into one list
    combined_posts = list(chain(text_posts, media_posts))
    
    # Sort posts by date_created, newest first
    author_posts_sorted = sorted(combined_posts, key=lambda post: post.date_created, reverse=True)
    
    followers = target_author.followers.all()
    following = target_author.following.all()
    friends = target_author.friends

    follow_requests_pending = False
    if viewer:
        follow_requests_pending = FollowRequest.objects.filter(actor=viewer, target=target_author).exists()

    return render(request, "author_profile.html", {
        "author": target_author,
        "viewer": viewer,
        "posts": author_posts_sorted,
        "followers": followers,
        "following": following,
        "friends": friends,
        "follow_requests_pending": follow_requests_pending,
    })


    is_following = False
    if viewer:
        is_following = target_author.uuid in viewer.following.values_list("uuid", flat=True)

    return render(request, "author_profile.html", {
        "author": target_author,
        "viewer": viewer,
        "posts": author_posts_sorted,
        "followers": followers,
        "following": following,
        "friends": friends,
        "follow_requests_pending": follow_requests_pending,
        "is_following": is_following,
    })

@user_controller(must_be_logged_in=True, must_be_author=True)
def local_author_modify_view(request: HttpRequest, target_author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """Modify `target_author_uuid`'s profile"""
    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    if viewer != target_author and not request.user.is_superuser:
        return HttpResponse("You do not have permission to modify this author", status=403)
    return render(request, "local_author_modify.html", {"author": target_author, "viewer": viewer})

# Views for Posts


@user_controller(must_be_logged_in=True, must_be_author=True)
def create_post_view(request: HttpRequest, viewer: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to create a post."""
    return render(request, "create_post.html", {"author": viewer})


@user_controller(must_be_logged_in=True, must_be_author=True)
def edit_post_view(request: HttpRequest, post_uuid: str, viewer: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to edit their post and toggle between Plain Text and Markdown."""

    post = get_object_or_404(models.PostTextBased, uuid=post_uuid)

    # only the author of the post can edit
    if post.author != viewer:
        return HttpResponse("You do not have permission to edit this post.", status=403)

    return render(request, "edit_post.html", {"post": post, "author": viewer})

@user_controller(must_be_logged_in=True, must_be_author=True)
def followers_list_view(request: HttpRequest, author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View the list of followers for a given author"""
    author = get_object_or_404(models.LocalAuthor, uuid=author_uuid)
    followers = models.LocalAuthor.objects.filter(following=author)
    return render(request, "followers_list.html", {"author": author, "viewer": viewer, "followers": followers})



@user_controller(must_be_logged_in=True, must_be_author=True)
def following_list_view(request: HttpRequest, author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View the list of users an author is following"""
    author = get_object_or_404(models.LocalAuthor, uuid=author_uuid)
    following = models.LocalAuthor.objects.filter(uuid__in=author.following.values_list("uuid", flat=True))
    return render(request, "following_list.html", {"author": author, "viewer": viewer, "following": following})


@user_controller(must_be_logged_in=True, must_be_author=True)
def friends_list_view(request: HttpRequest, author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View the list of friends (mutual followers) for a given author"""
    author = get_object_or_404(models.LocalAuthor, uuid=author_uuid)
    friends = models.LocalAuthor.objects.filter(uuid__in=[friend.uuid for friend in author.friends])
    return render(request, "friends_list.html", {"author": author, "viewer": viewer,"friends": friends})



def follow_requests_page(request: HttpRequest) -> HttpResponse:
    """
    Displays a page with the user's pending follow requests.

    Returns:
        HttpResponse: Rendered follow requests page, or redirects if user is not authenticated.
    """
    if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
        return HttpResponse("Unauthorized: Please log in to view follow requests.", status=401)

    current_author = request.user.author
    follow_requests = FollowRequest.objects.filter(target=current_author)
    return render(request, "follow_requests.html", {"follow_requests": follow_requests})

def search_authors_view(request: HttpRequest) -> JsonResponse:
    """
    Handles searching for authors by username or display name.

    Returns:
        JsonResponse: JSON response containing a list of matching authors.
    """
    query = request.GET.get("q", "")
    if query:
        authors = LocalAuthor.objects.filter(Q(user__username__icontains=query) | Q(display_name__icontains=query))
        results = [{"uuid": str(author.uuid), "username": author.user.username, "display_name": author.display_name} for author in authors]
    else:
        results = []

    return JsonResponse({"authors": results})
