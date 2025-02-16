from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file

from django.urls import reverse
from django.contrib.auth import authenticate, login

# General Views

def stream_view(request:HttpRequest) -> HttpResponse:
    """An author's stream"""
    if not request.user.is_authenticated:
        return render(request, "registration/not_logged_in.html")
    return render(request, "stream.html", {"user": request.user})


# Views for Authors

# Views for Posts
