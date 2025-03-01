from django.urls import path
from django.views.generic import RedirectView, TemplateView
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

    path("unauthorized",
         TemplateView.as_view(template_name="registration/unauthorized.html"),
         name="unauthorized")

]

urlpatterns_api = [
    path("api/post/delete/<uuid:post_uuid>",
         views_api.api_post_delete,
         name="api_post_delete"),

    path("api/post/edit/<uuid:post_uuid>",
         views_api.api_textpost_update,
         name="api_textpost_update"),

    path("api/create_text_post",
         views_api.api_textpost_create,
         name="api_textpost_create"),

    path("api/author/update/<uuid:target_author_uuid>",
         views_api.api_author_update,
         name="api_author_update"),


]

urlpatterns.extend(urlpatterns_api)
