from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "socialnetwork"
urlpatterns = [
    path("", RedirectView.as_view(url="stream")),
    path("not_logged_in", views.not_logged_in_view, name="not_logged_in"),
    path("stream", views.stream_view, name="stream"),
    path("author/<uuid:target_author_uuid>", views.author_profile_view, name="author_profile"),
    path("api/create_text_post/<str:post_type>", views.api_create_text_post, name="api_create_text_post"),
]