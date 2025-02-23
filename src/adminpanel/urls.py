from django.urls import path
from . import views

app_name = "adminpanel"
urlpatterns = [
    path("", views.adminpanel_view, name="adminpanel"),
    path("api/create_user", views.api_create_user, name="api_create_user"),
    path("api/create_author_for_superuser", views.api_create_author_for_superuser, name="api_create_author_for_superuser"),
    path("api/create_join_request", views.api_create_join_request, name="api_create_join_request"),
    path("api/join_request/<int:join_request_id>/approve", views.api_join_request_approve, name="api_join_request_approve"),
    path("api/join_request/<int:join_request_id>/deny", views.api_join_request_deny, name="api_join_request_deny"),
    path("api/join_request/<int:join_request_id>/undeny", views.api_join_request_undeny, name="api_join_request_undeny"),
    path("api/join_request/<int:join_request_id>/delete", views.api_join_request_delete, name="api_join_request_delete"),
    path('hosted_images/', views.hosted_images, name='hosted_images'),
    path('hosted_images/delete/<int:image_id>/', views.delete_hosted_image, name='delete_hosted_image'),
]