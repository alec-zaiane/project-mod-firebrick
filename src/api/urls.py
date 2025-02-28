from django.urls import path
from .views import *

from drf_spectacular import views as spectacular_views

app_name = "api"
urlpatterns = [
    path("schema/", spectacular_views.SpectacularSwaggerView.as_view(), name="schema"),
]
