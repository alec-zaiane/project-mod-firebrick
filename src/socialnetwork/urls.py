from django.urls import path
from django.views.generic import RedirectView, TemplateView
from . import views
from . import views_api

from django.conf import settings
from django.conf.urls.static import static


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
    path("api/v1/post/delete/<uuid:post_uuid>",
         views_api.api_post_delete,
         name="api_post_delete"),

    path("api/v1/post/edit/<uuid:post_uuid>",
         views_api.api_textpost_update,
         name="api_textpost_update"),

    path("api/v1/create_text_post",
         views_api.api_textpost_create,
         name="api_textpost_create"),

    path("api/v1/author/update/<uuid:target_author_uuid>",
         views_api.api_author_update,
         name="api_author_update"),

     path("api/v1/create_image_post",
          views_api.api_imagepost_create,
          name="api_imagepost_create"),



]

urlpatterns.extend(urlpatterns_api)
""" Ensures all routes are registerd before adding static file serving (runs only in development)"""
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
