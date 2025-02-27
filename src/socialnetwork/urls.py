from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import views_api

app_name = "socialnetwork"
urlpatterns = [
    path("", RedirectView.as_view(url="stream")),

    path("not_logged_in",
         views.not_logged_in_view,
         name="not_logged_in"),

    path("stream",
         views.stream_view,
         name="stream"),

    path("author/<uuid:target_author_uuid>",
         views.author_profile_view,
         name="author_profile"),

    path("author/<uuid:target_author_uuid>/modify",
         views.local_author_modify_view,
         name="author_modify"),

    path("create_post",
         views.create_post_view,
         name="author_create_post"),

    path("edit_post/<uuid:post_uuid>",
         views.edit_post_view,
         name="edit_post"),


]

urlpatterns_api = [
    path("api/post/delete/<uuid:post_uuid>",
         views_api.api_post_delete,
         name="api_post_delete"),

    path("api/create_text_post",
         views_api.api_create_text_post,
         name="api_create_text_post"),

    path("api/author/update/<uuid:target_author_uuid>",
         views_api.api_author_update,
         name="api_author_update"),
    
    path("api/post/edit/<uuid:post_uuid>",
         views.edit_post_view, # separate the API part into its own view
         name="api_post_edit"),

]

urlpatterns.extend(urlpatterns_api)
