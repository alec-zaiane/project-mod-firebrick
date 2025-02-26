from django.urls import path
from . import views
from . import views_api

app_name = "adminpanel"
urlpatterns = [
    path("",
         views.adminpanel_view,
         name="adminpanel"),

    path("hosted_images/",
         views.hosted_image_view,
         name="hosted_images"),

]

urlpatterns_api = [
    path("api/authors/create",
         views_api.author_create,
         name="api_author_create"),

    path("api/authors/create_for_superuser",
         views_api.author_create_for_superuser,
         name="api_author_create_for_superuser"),

    path("api/authors/<uuid:author_uuid>/delete",
         views_api.api_delete_author,
         name="api_author_delete"),

    path("api/join_request/create",
         views_api.api_create_join_request,
         name="api_create_join_request"),

    path("api/join_request/<int:join_request_id>/approve",
         views_api.api_join_request_approve,
         name="api_join_request_approve"),

    path("api/join_request/<int:join_request_id>/deny",
         views_api.api_join_request_deny,
         name="api_join_request_deny"),

    path("api/join_request/<int:join_request_id>/undeny",
         views_api.api_join_request_undeny,
         name="api_join_request_undeny"),

    path("api/join_request/<int:join_request_id>/delete",
         views_api.api_join_request_delete,
         name="api_join_request_delete"),

    path('api/hosted_images/',
         views_api.api_hosted_images,
         name='api_hosted_images'),

    path('api/hosted_images/<int:image_id>/delete',
         views_api.api_delete_hosted_image,
         name='api_hosted_image_delete'),

    path("hosted_images/public/",
         views.public_hosted_images,
         name="public_hosted_images"),
]

urlpatterns.extend(urlpatterns_api)
