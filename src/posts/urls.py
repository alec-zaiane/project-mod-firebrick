from rest_framework import routers
from django.urls import URLPattern, URLResolver, path

from posts.viewsets import PostViewSet  # Import PostViewSet from posts.viewsets
from posts import views


app_name = "posts"
urlpatterns: list[URLPattern | URLResolver] = [
    path('stream/',
         views.stream_view,
         name='stream'),
]

# DRF Router to automatically generate CRUD API endpoints
router = routers.SimpleRouter()
router.register(r"api/posts", PostViewSet)  # Registers /posts/ as an API route

urlpatterns += router.urls  # Add all generated routes
