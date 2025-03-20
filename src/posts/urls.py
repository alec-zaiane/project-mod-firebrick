from rest_framework import routers
from django.urls import URLPattern, URLResolver, path

from posts.viewsets import PostViewSet  # Import PostViewSet from posts.viewsets
from posts import views

from django.views import generic
from posts.models import Post

app_name = "posts"
urlpatterns: list[URLPattern | URLResolver] = [
    path('stream/',
         views.stream_view,
         name='stream'),

    path("posts/<uuid:post_uuid>/", 
         views.view_post, 
         name="view_post"),

    path('post/<uuid:post_uuid>/',  # TODO please completely overwrite this! it's only here for name=edit_post to exist while it's not set up yet
         generic.TemplateView.as_view(template_name="components/post_card.html"),
         name="edit_post"),

]

# DRF Router to automatically generate CRUD API endpoints
router = routers.SimpleRouter()
# Registers /posts/ as an API route
router.register(r"api/posts", PostViewSet, basename="api_posts")

urlpatterns += router.urls  # Add all generated routes

print(urlpatterns)
