from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status


from posts.models import Post
from posts.serializers import PostSerializer
from posts.permissions import PostPermission


class PostViewSet(viewsets.ModelViewSet[Post]):
    """ViewSet for handling posts (text & image)
       This viewset supports standard CRUD (read is auto handles by REST btw) Operations:
       The issue I got was that the default delete wasn't soft delete,
       instead we're using a custom decorator to soft delete

       - Create: attaches the current user's author instance w perform_create
       - Update: only allows authors to modify their own post
       - Soft Delete: performs soft delete instead of a hard delete
    """

    queryset = Post.visible_posts.all()
    serializer_class = PostSerializer
    Permission_classes = [IsAuthenticated, PostPermission]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        """Override create to attach the current user as the author.
           This ensures all posts are linked correctly while allowing proper validation.
        """
        data = request.data.copy()
        data["author"] = request.user.author

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Override update to ensure only authors can modify their posts"""
        post = self.get_object()
        if post.author != request.user.author:
            return Response({"error": "You cannot edit someone else's post"}, status=403)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        """
        Soft delete the specified post.

        Instead of permanently deleting the post, this action marks the post as soft-deleted.
        Only the author of the post is allowed to di this.
        """
        post = self.get_object()
        if post.author != request.user.author:
            return Response(
                {"error": "You cannot delete someone else's post"},
                status=status.HTTP_403_FORBIDDEN
            )
        post.soft_delete()
        return Response({"detail": "Post soft deleted"}, status=status.HTTP_204_NO_CONTENT)
