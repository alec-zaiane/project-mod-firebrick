from typing import Any, Literal, Optional

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.urls import reverse

from socialnetwork.utils.user_control_decorator import user_control
from . import models
from . import serializers

from .forms import PostTextBasedForm  


# General Views

def not_logged_in_view(request:HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")

@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def stream_view(request:HttpRequest, author:models.LocalAuthor) -> HttpResponse:
    """An author's stream view"""
    page = int(request.GET.get('page', '1'))
    size = int(request.GET.get('size', '10'))
    start = (page - 1) * size
    
    posts = author.get_stream(paginate_start=start, paginate_count=size)
    
    return render(request, "stream.html", {
        "user": request.user,
        "author": author,
        "posts": posts,
        "current_page": page,
    })


@user_control(can_be_author=True, can_be_logged_out=True, can_be_superuser=True)
def author_profile_view(request: HttpRequest, target_author_uuid: str, author: Optional[models.LocalAuthor] = None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""

    target_author = get_object_or_404(models.LocalAuthor, uuid=target_author_uuid)
    author_posts = models.PostTextBased.objects.filter(base_author=target_author)

    return render(request, "author_profile.html", {"author": target_author, "viewer": author, "posts": author_posts})


# Views for Posts
@api_view(["POST"])
@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def api_create_text_post(request:Request, author:models.LocalAuthor, post_type:Literal["plaintext", "commonmark"]) -> Response|HttpResponseRedirect:
    """Create a text based post"""
    if post_type not in ("plaintext", "commonmark"):
        return Response({"error": "Invalid type"}, status=400)
    
    data:dict[str,Any] = request.data # type: ignore # missing stub file
    data["author"] = author.uuid
    if post_type == "plaintext":
        data["post_type"] = models.PostTextBased.TextPostTypes.PLAINTEXT
    elif post_type == "commonmark":
        data["post_type"] = models.PostTextBased.TextPostTypes.MARKDOWN
    
    serializer = serializers.PostTextBasedSerializer(data=data)
    
    # save it all
    if serializer.is_valid():
        post:models.PostTextBased = serializer.save() # type: ignore # missing stub file
        post.send_to_required_private_inboxes()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

@api_view(["PUT","PATCH"])
@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=True)
def api_author_update(request:Request, author:models.LocalAuthor, target_author_uuid:str) -> Response:
    """Update an author's information, **author kwarg is not the target author, but the viewer author**
    Only an admin or the author themselves can update their information"""
    target_author = get_object_or_404(models.LocalAuthor, uuid=target_author_uuid)
    if author != target_author and not author.user.is_superuser:
        return Response({"error": "You do not have permission to update this author"}, status=403)
    serializer = serializers.AuthorSerializer(target_author, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
    
    
    

@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def create_post_view(request: HttpRequest, author: models.LocalAuthor) -> HttpResponse:
    """Render a form for authors to create a post."""
    
    if request.method == "POST":
        form = PostTextBasedForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # Ensure post is linked to the logged-in author
            post.author = author  
            post.save()
            post.send_to_required_private_inboxes()
            # Redirect to stream after posting
            return redirect("socialnetwork:stream")  

    else:
        form = PostTextBasedForm()

    return render(request, "author_create_post.html", {"form": form, "author": author})