from typing import Optional

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from socialnetwork.utils.user_control_decorator import user_control
# from rest_framework.decorators import api_view
# from rest_framework.request import Request
# from rest_framework.response import Response

from django.contrib.auth.models import AnonymousUser
from socialnetwork import models as socialmodels
from .models import AuthorJoinRequest


# Create your views here.
# This file is for views that show browser output (eg: render a template), use views_api.py for rest_framework API views
UNAUTHENTICATED_RESPONSE = HttpResponseRedirect(
    reverse("socialnetwork:not_logged_in"))


@user_control(must_be_logged_in=True, must_be_superuser=True)
def adminpanel_view(request: HttpRequest, viewer: Optional[socialmodels.LocalAuthor]) -> HttpResponse:
    if isinstance(request.user, AnonymousUser):  # can't happen, needed for mypy
        return UNAUTHENTICATED_RESPONSE
    requests_active = AuthorJoinRequest.objects.filter(date_denied=None)
    requests_denied = AuthorJoinRequest.objects.exclude(date_denied=None)
    viewer_has_an_author = viewer is not None
    viewer
    return render(request, "adminpanel.html", {
        "viewer_has_an_author": viewer_has_an_author,
        "viewer_author": viewer,
        "requests_active": requests_active,
        "requests_denied": requests_denied,
        "current_authors_local": socialmodels.LocalAuthor.objects.all(),
        "current_authors_remote": socialmodels.RemoteAuthor.objects.all(),
    })


@user_control(must_be_logged_in=True, must_be_superuser=True)
def hosted_image_view(request: HttpRequest) -> HttpResponse:
    all_hosted_images = socialmodels.HostedImage.objects.all()
    return render(request, "hosted_images.html", {
        "images": all_hosted_images
    })


@user_control(must_be_logged_in=True)
def public_hosted_images(request: HttpRequest) -> HttpResponse:
    """
    A public view listing all hosted images, so regular users can copy their URLs.
    """
    images = socialmodels.HostedImage.objects.all().order_by("-uploaded_at")
    return render(request, "public_hosted_images.html", {"images": images})
