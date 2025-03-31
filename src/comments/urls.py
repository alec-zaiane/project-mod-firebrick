from rest_framework import routers
from django.urls import URLPattern, URLResolver, path

from comments.viewsets import CommentViewSet

from comments.views import InternalCommentView
from comments.views import PostCommentsAPIView

app_name = "comments"
urlpatterns: list[URLPattern | URLResolver] = [
    path("comments/<str:encoded_post_fqid>/", InternalCommentView.as_view(), name="internal_comment"),
    path("posts/<str:post_fqid>/comments", PostCommentsAPIView.as_view(), name="node2node_post_comments"),
]

router = routers.SimpleRouter()
router.register(r"api/comments", CommentViewSet, basename="node2node_comments")

urlpatterns += router.urls
