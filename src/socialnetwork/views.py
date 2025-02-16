from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file

from django.urls import reverse
from django.contrib.auth import authenticate, login

# General Views

def not_logged_in_view(request:HttpRequest) -> HttpResponse:
    """A view for users who are not logged in."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:home"))
    return render(request, "registration/not_logged_in.html")

def stream_view(request:HttpRequest) -> HttpResponse:
    """An author's stream view, checks if the user is logged in or is a superuser, only non-superusers get a stream view."""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
    return render(request, "stream.html", {"user": request.user})


# Views for Authors

# Views for Posts
