# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpRequest, HttpResponse
# from django.contrib.auth.decorators import login_required
# # same thing here as I stated in views_api.py
# from user_management.models import LocalAuthor

# # Create your views here.

# @login_required
# def create_post_view(request: HttpRequest) -> HttpResponse:
#     "Render a form for authors to create a PT or MD post"
#     viewer = request.user.author
#     return render(request, "posts/create_post.html", {"author": viewer})


# @login_required
# def edit_post_view(request: HttpRequest, post_uuid: str) -> HttpResponse:
#     "Render a form for authors to edit their posts, can toggle btwn PT and MD still"
#     post = get_object_or_404(Post, uuid=post_uuid)
#     viewer = request.user.author
#     if post.author != request.user.author:
#         return HttpResponse("You cannot modify a post that isn't yours ")
#     # this goes to edit_post_view actually
#     return render(request, "posts/create_post.html", {"author":viewer})

# @login_required
# def view_post(request: HttpRequest, post_uuid: str) -> HttpResponse:
#     """View a post based on its UUID."""
#     post = get_object_or_404(Post, uuid=post_uuid)

#     if not Post.visible_posts.get_posts_visible_to_author(request.user.author).filter(uuid=post_uuid).exists():
#         return HttpResponse("You do not have permission to view this post.", status=403)

#     return render(request, "posts/view_post.html", {"post": post, "viewer": request.user.author})
