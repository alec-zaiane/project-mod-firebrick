from typing import Any, Literal, Optional

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file

from django.urls import reverse
from django.contrib.auth import authenticate, login

from socialnetwork.utils.user_control_decorator import user_control
from . import models
from . import serializers

# General Views

def not_logged_in_view(request:HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")

@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def stream_view(request:HttpRequest, author:models.LocalAuthor) -> HttpResponse:
    """
    An author's stream view.
    For non-admin users, filter out posts that are marked as deleted.
    """
    if request.user.is_staff:
        posts = models.PostTextBased.objects.all().order_by('date_created')
    else:
        posts = models.PostTextBased.objects.filter(is_deleted=False).order_by('date_created')
    
    return render(request, "stream.html", {"author": author, "posts": posts})

# Views for Authors
@user_control(can_be_author=True, can_be_logged_out=True, can_be_superuser=True)
def author_profile_view(request:HttpRequest, target_author_uuid:str, author:Optional[models.LocalAuthor]=None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""
    target_author = get_object_or_404(models.LocalAuthor, uuid=target_author_uuid)
    return render(request, "author_profile.html", {"author": target_author, "viewer": author})

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