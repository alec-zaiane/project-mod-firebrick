from typing import Any

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from socialnetwork.utils.user_control_decorator import user_control
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file

from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, RemoteAuthor
from .models import AuthorJoinRequest

from .serializers import AuthorJoinRequestSerializer

# Create your views here.
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def adminpanel_view(request:HttpRequest) -> HttpResponse:
    requests_active = AuthorJoinRequest.objects.filter(date_denied=None)
    requests_denied = AuthorJoinRequest.objects.exclude(date_denied=None)
    return render(request, "adminpanel.html", {
        "requests_active": requests_active,
        "requests_denied": requests_denied,
        "current_authors_local": LocalAuthor.objects.all(),
        "current_authors_remote": RemoteAuthor.objects.all(),
    })



# API views
@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_create_user(request:Request) -> Response|HttpResponse:
    username = request.data.get("username", None) # type: ignore # missing stub file
    password = request.data.get("password", None) # type: ignore # missing stub file
    if not isinstance(username, str) or not isinstance(password, str):
        return Response({"error": "`username` and `password` fields must provided and be strings"}, status=400)
    if not username or not password:
        return Response({"error": "`username` and `password` fields must be non-empty"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)
    # Creating a join request to do this might be overkill, but it keeps the code in one place
    join_request = AuthorJoinRequest(username=username, password=password)
    if join_request.get_validity_errors():
        join_request.delete()
        return Response({"error": "Invalid request", "invalid": join_request.get_validity_errors()}, status=400)
    join_request.approve_and_create()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
    # return Response({"success": "User created", "uuid": author.uuid}, status=201)

## Join request API   
@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=True, can_be_superuser=True)
def api_create_join_request(request:Request) -> Response|HttpResponse:
    if not hasattr(request, "data"):
        return Response({"error": "Request must have a JSON body"}, status=400)
    data:dict[str,Any] = request.data # type: ignore # missing stub file
    serializer = AuthorJoinRequestSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    serializer.save() # type: ignore # missing stub file
    return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_approve(request:Request, join_request_id:int) -> Response|HttpResponse:
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    try:
        join_request.approve_and_create()
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_deny(request:Request, join_request_id:int) -> Response|HttpResponse:
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    join_request.deny()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_undeny(request:Request, join_request_id:int) -> Response|HttpResponse:
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    join_request.undeny()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_delete(request:Request, join_request_id:int) -> Response|HttpResponse:
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    if not join_request.is_denied:
        return Response({"error": "Only denied requests can be deleted"}, status=400)
    join_request.delete()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
