from django.urls import path
from . import views

app_name = "adminpanel"
urlpatterns = [
    path("", views.adminpanel_view, name="adminpanel"),
]