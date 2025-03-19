from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View

from user_management.forms import JoinRequestForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from user_management.models import Author, FollowRequest
from user_management.serializers import FollowRequestSerializer
from typing import Optional

# Create your views here.

class JoinView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = JoinRequestForm()
        return render(request, "registration/join.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = JoinRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "registration/join_success.html")
        return render(request, "registration/join.html", {"form": form})

class FollowRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, format: Optional[str] = None) -> Response:
        # check if the user is authenticated
        if request.user.is_anonymous:
            return Response(
                {"error": "User must be authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            follower = request.user.author
        except AttributeError:
            return Response(
                {"error": "User is not linked to an author."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # expect a POST field 'followee_id' with the target author's UUID
        followee_id = request.data.get("followee_id")
        if not followee_id:
            return Response(
                {"error": "Field 'followee_id' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # find target author
        try:
            followee = Author.objects.get(uuid=followee_id)
        except Author.DoesNotExist:
            return Response(
                {"error": "Target author not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ensure the target is a local author
        if not followee.is_local:
            return Response(
                {"error": "Target author is not local."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create the follow request
        follow_request = FollowRequest.objects.create_follow_request(follower, followee)
        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
