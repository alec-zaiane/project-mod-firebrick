from rest_framework import routers
from posts.viewsets import PostViewSet  # Import PostViewSet from posts.viewsets

app_name = "posts"
urlpatterns = []

# DRF Router to automatically generate CRUD API endpoints
router = routers.SimpleRouter()
router.register(r"posts", PostViewSet)  # Registers /posts/ as an API route

urlpatterns += router.urls  # Add all generated routes
