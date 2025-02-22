from django.urls import path
from . import views

app_name = "adminpanel"
urlpatterns = [
    path("", views.adminpanel_view, name="adminpanel"),
    
    path("api/authors/create", views.author_create, name="api_author_create"),
    path("api/authors/create_for_superuser", views.author_create_for_superuser, name="api_author_create_for_superuser"),
    path("api/authors/<uuid:author_uuid>/delete", views.api_delete_author, name="api_author_delete"),
    
    
    path("api/join_request/create", views.api_create_join_request, name="api_create_join_request"),
    path("api/join_request/<int:join_request_id>/approve", views.api_join_request_approve, name="api_join_request_approve"),
    path("api/join_request/<int:join_request_id>/deny", views.api_join_request_deny, name="api_join_request_deny"),
    path("api/join_request/<int:join_request_id>/undeny", views.api_join_request_undeny, name="api_join_request_undeny"),
    path("api/join_request/<int:join_request_id>/delete", views.api_join_request_delete, name="api_join_request_delete"),
    
]