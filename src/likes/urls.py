from rest_framework import routers
from django.urls import URLPattern, URLResolver, path

from likes.viewsets import LikeViewSet
from likes import views

app_name = "likes"
urlpatterns: list[URLPattern | URLResolver] = [
    path("api/likes/<str:target_fqid>/like", views.LikeByViewer.as_view(), name="like_by_viewer"),
]

router = routers.SimpleRouter()
router.register(r"api/likes", LikeViewSet, basename="node2node_likes")

urlpatterns += router.urls
