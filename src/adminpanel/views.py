from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from socialnetwork.utils.user_control_decorator import user_control
from rest_framework.decorators import api_view # type: ignore # missing stub file
from rest_framework.request import Request # type: ignore # missing stub file
from rest_framework.response import Response # type: ignore # missing stub file

from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor
from .models import AuthorJoinRequest

# Create your views here.
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def adminpanel_view(request:HttpRequest) -> HttpResponse:
    return render(request, "adminpanel.html")



# API views
@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_create_user(request:Request) -> Response:
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
    author = join_request.approve_and_create()
    return Response({"success": "User created", "uuid": author.uuid}, status=201)