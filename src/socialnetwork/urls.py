from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "socialnetwork"
urlpatterns = [
    path("", RedirectView.as_view(url="stream")),
    path("not_logged_in", views.not_logged_in_view, name="not_logged_in"),
    path("stream", views.stream_view, name="stream"),
    path("author/<uuid:target_author_uuid>", views.author_profile_view, name="author_profile"),
    path("author/<uuid:target_author_uuid>/modify", views.local_author_modify_view, name="author_modify"),
    path("create_post", views.create_post_view, name="author_create_post"),
    
    path("api/create_text_post", views.api_create_text_post, name="api_create_text_post"),
    path("api/author/update/<uuid:target_author_uuid>", views.api_author_update, name="api_author_update"),
    path("edit_post/<uuid:post_uuid>", views.edit_post_view, name="edit_post"),
]