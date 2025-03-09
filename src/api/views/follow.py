from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, FollowRequest
from socialnetwork.serializers import FollowRequestSerializer
from api.serializers.author_serializers import AuthorSerializer  # Assuming this exists
from django.http import HttpRequest


# ✅ Helper function to get the LocalAuthor from request
def get_authenticated_author(request: HttpRequest) -> LocalAuthor | Response:
    """
    Returns the LocalAuthor associated with the authenticated user.
    If the user is not authenticated, returns a 401 Unauthorized response.
    """
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    # Ensure the user is linked to an author
    if not hasattr(request.user, "author"):
        return Response({"error": "User does not have an associated author."}, status=status.HTTP_400_BAD_REQUEST)

    return request.user.author


# 1. Send a Follow Request
class SendFollowRequestView(APIView):
    def post(self, request: HttpRequest, target_id: str) -> Response:
        requester = get_authenticated_author(request)
        if isinstance(requester, Response):
            return requester  # If an error response was returned, send it

        target = get_object_or_404(LocalAuthor, uuid=target_id)
        if FollowRequest.objects.filter(actor=requester, target=target).exists():
            return Response({"detail": "Follow request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        follow_request = FollowRequest.objects.create(actor=requester, target=target)
        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 2. Approve a Follow Request
class ApproveFollowRequestView(APIView):
    def post(self, request: HttpRequest, request_id: str) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        follow_request = get_object_or_404(FollowRequest, uuid=request_id, target=current_author)
        follow_request.actor.following.add(current_author)
        follow_request.delete()
        return Response({"detail": "Follow request approved."}, status=status.HTTP_200_OK)


# 3. Deny a Follow Request
class DenyFollowRequestView(APIView):
    def post(self, request: HttpRequest, request_id: str) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        follow_request = get_object_or_404(FollowRequest, uuid=request_id, target=current_author)
        follow_request.delete()
        return Response({"detail": "Follow request denied."}, status=status.HTTP_200_OK)


# 4. Unfollow an Author
class UnfollowView(APIView):
    def delete(self, request: HttpRequest, target_id: str) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        target = get_object_or_404(LocalAuthor, uuid=target_id)
        if not current_author.following.filter(uuid=target.uuid).exists():
            return Response({"detail": "Not following this author."}, status=status.HTTP_400_BAD_REQUEST)

        current_author.following.remove(target)
        return Response({"detail": "Successfully unfollowed."}, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest, target_id: str) -> Response:
        return self.delete(request, target_id)


# 5. List Incoming Follow Requests
class ListFollowRequestsView(APIView):
    def get(self, request: HttpRequest) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        follow_requests = FollowRequest.objects.filter(target=current_author)
        serializer = FollowRequestSerializer(follow_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 6. List Followers
class ListFollowersView(APIView):
    def get(self, request: HttpRequest) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        serializer = AuthorSerializer(current_author.followers.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 7. List Following
class ListFollowingView(APIView):
    def get(self, request: HttpRequest) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        serializer = AuthorSerializer(current_author.following.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 8. List Friends (Mutual Followers)
class ListFriendsView(APIView):
    def get(self, request: HttpRequest) -> Response:
        current_author = get_authenticated_author(request)
        if isinstance(current_author, Response):
            return current_author

        following_set = set(current_author.following.all())
        followers_set = set(current_author.followers.all())
        friends = following_set.intersection(followers_set)
        serializer = AuthorSerializer(list(friends), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

