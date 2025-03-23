from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import View
from django.template import loader
from posts.forms import CreatePostForm
from posts.models import Post, PostTypes
from core.utils.redirects import REDIRECT_TO_LOGIN
from core.utils.request_viewer import get_request_viewer


# # Create your views here.

class CreatePostView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """Render a form for authors to create a PT or MD post"""
        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        form = CreatePostForm()
        return render(request, "create_post.html", {"form": form, "author": viewer})

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Creates a PT or MD post and submit it, then returning to where the user was before.
        """

        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = viewer
            post.host_node = viewer.host_node
            post.save()

            next_url = f"{reverse('posts:view_post', kwargs={'post_uuid': post.uuid})}?next={request.GET.get('next', '/')}"
            return HttpResponseRedirect(next_url)

        return render(request, "create_post.html", {"form": form, "author": viewer})


class EditPostView(View):
    def get(self, request: HttpRequest, post_uuid: str) -> HttpResponse:
        """Render a form for authors to edit their posts, can toggle btwn PT and MD still"""
        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        post = get_object_or_404(Post, uuid=post_uuid)
        if post.author != viewer:
            response = loader.render_to_string(
                "no-permission.html", {"error": "You do not have permission to edit this post.", "user": request.user, "post": post, "viewer": viewer})
            return HttpResponse(response, status=403)

        form = CreatePostForm(instance=post)
        return render(request, "edit_post.html", {"form": form, "author": viewer})

    def post(self, request: HttpRequest, post_uuid: str) -> HttpResponse:
        """
        Creates a PT or MD post and submit it, then returning to where the user was before.
        """

        viewer = get_request_viewer(request)
        if viewer is None:
            return REDIRECT_TO_LOGIN(request)

        post = get_object_or_404(Post, uuid=post_uuid)
        if post.author != viewer:
            response = loader.render_to_string(
                "no-permission.html", {"error": "You do not have permission to edit this post.", "user": request.user, "post": post, "viewer": viewer})
            return HttpResponse(response, status=403)

        form = CreatePostForm(request.POST, instance=post)
        form.instance.author = viewer
        form.instance.host_node = viewer.host_node
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.GET.get('next', '/'))

        return render(request, "edit_post.html", {"form": form, "author": viewer})


class ViewPostView(View):
    def get(self, request: HttpRequest, post_uuid: str) -> HttpResponse:
        """View a post based on its UUID."""
        viewer = get_request_viewer(request)

        post = get_object_or_404(Post, uuid=post_uuid)

        if not viewer or not Post.visible_posts.get_posts_visible_to_author(viewer).filter(uuid=post_uuid).exists():
            response = loader.render_to_string(
                "no-permission.html", {"error": "You do not have permission to view this post.", "user": request.user, "post": post, "viewer": viewer})
            return HttpResponse(response, status=403)

        return render(request, "view_post.html", {"post": post, "viewer": viewer})


class StreamView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """Stream view for an author"""
        viewer = get_request_viewer(request)
        # TODO: this should work if the viewer is not an author
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
