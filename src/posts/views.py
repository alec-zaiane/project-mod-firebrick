from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from posts.models import Post
# same thing here as I stated in views_api.py
from user_management.models import LocalAuthor


from core.utils.user_control_decorator import user_control, user_controller, REDIRECT_TO_LOGIN


# Create your views here.

@login_required
def create_post_view(request: HttpRequest) -> HttpResponse:
    "Render a form for authors to create a PT or MD post"
    viewer = request.user.author
    return render(request, "posts/create_post.html", {"author": viewer})


@login_required
def edit_post_view(request: HttpRequest, post_uuid: str) -> HttpResponse:
    "Render a form for authors to edit their posts, can toggle btwn PT and MD still"
    post = get_object_or_404(Post, uuid=post_uuid)
    viewer = request.user.author
    if post.author != request.user.author:
        return HttpResponse("You cannot modify a post that isn't yours ")
    # this goes to edit_post_view actually
    return render(request, "posts/create_post.html", {"author": viewer})


@login_required
def view_post(request: HttpRequest, post_uuid: str) -> HttpResponse:
    """View a post based on its UUID."""
    post = get_object_or_404(Post, uuid=post_uuid)

    if not Post.visible_posts.get_posts_visible_to_author(request.user.author).filter(uuid=post_uuid).exists():
        return HttpResponse("You do not have permission to view this post.", status=403)

    return render(request, "posts/view_post.html", {"post": post, "viewer": request.user.author})


@user_controller(must_be_logged_in=True, fail_response=REDIRECT_TO_LOGIN)
def stream_view(request: HttpRequest, viewer: LocalAuthor) -> HttpResponse:
    """Stream view for an author"""
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
