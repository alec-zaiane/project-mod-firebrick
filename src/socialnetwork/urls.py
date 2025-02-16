from django.urls import path
from . import views

app_name = "socialnetwork"
urlpatterns = [
    path("", views.stream_view, name="stream"),
]