from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from posts.models import Post


from core.utils.redirects import REDIRECT_TO_LOGIN
from core.utils.request_viewer import get_request_viewer


# # Create your views here.

class CreatePostView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """Render a form for authors to create a PT or MD post"""
        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        return render(request, "create_post.html", {"author": viewer})


class EditPostView(View):
    def get(self, request: HttpRequest, post_uuid: str) -> HttpResponse:
        """Render a form for authors to edit their posts, can toggle btwn PT and MD still"""
        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        post = get_object_or_404(Post, uuid=post_uuid)
        if post.author != viewer:
            return render(request, "no_permission_edit.html", {"post": post, "viewer": viewer})

        return render(request, "edit_post.html", {"post": post, "author": viewer})


class ViewPostView(View):
    def get(self, request: HttpRequest, post_uuid: str) -> HttpResponse:
        """View a post based on its UUID."""
        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        post = get_object_or_404(Post, uuid=post_uuid)

        if not Post.visible_posts.get_posts_visible_to_author(viewer).filter(uuid=post_uuid).exists():
            return render(request, "no_permission_view.html", {"post": post, "viewer": viewer})

        return render(request, "view_post.html", {"post": post, "viewer": viewer})


class StreamView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
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
