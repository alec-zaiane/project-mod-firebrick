from django.shortcuts import render


from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from comments.serializers import CommentSerializer
from comments.models import Comment
from posts.models import Post, PostTypes
from core.utils.request_viewer import get_request_viewer


# Create your views here.


class InternalCommentView(APIView):
    def post(self, request: Request, encoded_post_fqid: str) -> Response:
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response({"detail": "not logged in as an author"}, status=401)
        post = Post.objects.find_by_encoded_fqid(encoded_post_fqid)
        if post is None or not post.check_can_be_seen_by(viewer):
            return Response({"detail": "post not found"}, status=404)
        comment_text = request.data.get("comment")
        if comment_text is None:
            return Response({"detail": "comment is required"}, status=400)
        Comment.objects.create_comment(viewer, post, comment_text, PostTypes.PLAINTEXT)
        return Response({"detail": "comment created"}, status=201)


class PostCommentsAPIView(APIView):
    def get(self, request: Request, encoded_post_fqid: str) -> Response:
        post = Post.objects.find_by_encoded_fqid(encoded_post_fqid)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post=post)
        return Response({
            "type": "comments",
            "post": post.fqid,
            "src": [CommentSerializer(c).data for c in comments]
        })
