from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from posts.models import Post


from core.utils.redirects import REDIRECT_TO_LOGIN
from core.utils.request_viewer import get_request_viewer


# # Create your views here.

@login_required
def create_post_view(request: HttpRequest) -> HttpResponse:
    "Render a form for authors to create a PT or MD post"
    viewer = get_request_viewer(request)
    if viewer is None:
        return REDIRECT_TO_LOGIN(request)
    return render(request, "posts/create_post.html", {"author": viewer})


@login_required
def edit_post_view(request: HttpRequest, post_uuid: str) -> HttpResponse:
    "Render a form for authors to edit their posts, can toggle btwn PT and MD still"
    viewer = get_request_viewer(request)
    if viewer is None:
        return REDIRECT_TO_LOGIN(request)
    post = get_object_or_404(Post, uuid=post_uuid)
    if post.author != viewer:
        return HttpResponse("You cannot modify a post that isn't yours ")
    # this goes to edit_post_view actually
    return render(request, "posts/create_post.html", {"author": viewer})


@login_required
def view_post(request: HttpRequest, post_uuid: str) -> HttpResponse:
    """View a post based on its UUID."""
    viewer = get_request_viewer(request)
    if viewer is None:
        return REDIRECT_TO_LOGIN(request)
    post = get_object_or_404(Post, uuid=post_uuid)

    # if not Post.visible_posts.get_posts_visible_to_author(viewer).filter(uuid=post_uuid).exists():
    #     return HttpResponse("You do not have permission to view this post.", status=403)
    if post.is_soft_deleted and not request.user.is_superuser:
        return HttpResponse("You do not have permission to view this post.", status=403)

    return render(request, "posts/view_post.html", {"post": post, "viewer": viewer})


@login_required
def stream_view(request: HttpRequest) -> HttpResponse:
    """Stream view for an author"""
    viewer = get_request_viewer(request)
    if viewer is None:
        return REDIRECT_TO_LOGIN(request)
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
