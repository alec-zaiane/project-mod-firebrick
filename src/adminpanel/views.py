from typing import Any, List, Dict

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet

from socialnetwork.utils.user_control_decorator import user_control
# from rest_framework.decorators import api_view
# from rest_framework.request import Request
# from rest_framework.response import Response

from django.contrib.auth.models import User, AnonymousUser
from socialnetwork import models as socialmodels
from .models import AuthorJoinRequest

from .serializers import AuthorJoinRequestSerializer
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
# This file is for views that show browser output (eg: render a template), use views_api.py for rest_framework API views


@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def adminpanel_view(request: HttpRequest) -> HttpResponse:
    # can't ever happen, but needed for type checker
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))
    requests_active = AuthorJoinRequest.objects.filter(date_denied=None)
    requests_denied = AuthorJoinRequest.objects.exclude(date_denied=None)
    viewer_has_an_author = socialmodels.LocalAuthor.objects.filter(
        user=request.user).exists()
    viewer_author = socialmodels.LocalAuthor.objects.get(
        user=request.user) if viewer_has_an_author else None
    return render(request, "adminpanel.html", {
        "viewer_has_an_author": viewer_has_an_author,
        "viewer_author": viewer_author,
        "requests_active": requests_active,
        "requests_denied": requests_denied,
        "current_authors_local": socialmodels.LocalAuthor.objects.all(),
        "current_authors_remote": socialmodels.RemoteAuthor.objects.all(),
    })


@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def hosted_image_view(request: HttpRequest) -> HttpResponse:
    all_hosted_images = socialmodels.HostedImage.objects.all()
    return render(request, "hosted_images.html", {
        "images": all_hosted_images
    })


def public_hosted_images(request: HttpRequest) -> HttpResponse:
    """
    A public view listing all hosted images, so regular users can copy their URLs.
    """
    images = socialmodels.HostedImage.objects.all().order_by("-uploaded_at")
    return render(request, "public_hosted_images.html", {"images": images})
