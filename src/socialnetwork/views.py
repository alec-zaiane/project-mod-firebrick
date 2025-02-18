from typing import Optional

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file

from django.urls import reverse
from django.contrib.auth import authenticate, login

from socialnetwork.utils.user_control_decorator import user_control
from . import models

# General Views

def not_logged_in_view(request:HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")

@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def stream_view(request:HttpRequest, author:models.LocalAuthor) -> HttpResponse:
    """An author's stream view"""
    return render(request, "stream.html", {"author": author})

# Views for Authors
@user_control(can_be_author=True, can_be_logged_out=True, can_be_superuser=True)
def author_profile_view(request:HttpRequest, target_author_uuid:str, author:Optional[models.LocalAuthor]=None) -> HttpResponse:
    """View `target_author_uuid`'s profile"""
    target_author = get_object_or_404(models.LocalAuthor, uuid=target_author_uuid)
    return render(request, "author_profile.html", {"author": target_author, "viewer": author})

# Views for Posts
