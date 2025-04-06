from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from django.urls import URLPattern, URLResolver, path

from posts.views import CreatePostView, EditPostView, StreamView, ViewPostView
from posts.viewsets import PostViewSet, AuthorPostViewSet  # Import PostViewSet from posts.viewsets

from django.views import generic
from posts.models import Post

app_name = "posts"
urlpatterns: list[URLPattern | URLResolver] = [
    path('stream/',
         StreamView.as_view(),
         name='stream'),
    path('create_post/',
         CreatePostView.as_view(),
         name='create_post'),
    path('post/<uuid:post_uuid>/',
         ViewPostView.as_view(),
         name="view_post"),
    path('post/<uuid:post_uuid>/edit/',
         EditPostView.as_view(),
         name="edit_post"),

]

# DRF Router to automatically generate CRUD API endpoints
router = routers.SimpleRouter()

# Registers /posts/ as an API route
router.register(r"api/posts", PostViewSet, basename="api_posts")

author_router = nested_routers.NestedSimpleRouter(
     router,
     r"/api/authors",
     lookup="author",
)
author_router.register(
    r"posts",
    AuthorPostViewSet,
    basename="node2node_authors_posts",
)


urlpatterns += router.urls  # Add all generated routes
