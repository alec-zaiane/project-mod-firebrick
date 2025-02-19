from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

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
    return render(request, "stream.html", {"user": request.user})

# Views for Authors

# Views for Posts
