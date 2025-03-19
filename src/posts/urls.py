from rest_framework import routers
from django.urls import URLPattern, URLResolver, path

from posts.viewsets import PostViewSet  # Import PostViewSet from posts.viewsets
from posts import views


app_name = "posts"
urlpatterns: list[URLPattern | URLResolver] = [
    path('stream/',
         views.stream_view,
         name='stream'),
    path("posts/<uuid:post_uuid>/", views.view_post, name="view_post"),
]

# DRF Router to automatically generate CRUD API endpoints
router = routers.SimpleRouter()
router.register(r"posts", PostViewSet)  # Registers /posts/ as an API route

urlpatterns += router.urls  # Add all generated routes
