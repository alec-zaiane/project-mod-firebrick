from django.urls import path
from .views import *

from django.views import View

from drf_spectacular import views as spectacular_views

app_name = "api"
urlpatterns = [
    path("", View.as_view(), name="root"),
    # Schema views
    path("schema/",
         spectacular_views.SpectacularAPIView.as_view(),
         name="schema"),
    path("schema/swagger-ui/",
         spectacular_views.SpectacularSwaggerView.as_view(url_name="api:schema"),  # noqa
         name="swagger-ui"),
    path("schema/redoc/",
         spectacular_views.SpectacularRedocView.as_view(url_name="api:schema"),
         name="redoc"),

    # Author views
    path("authors", AuthorsView.as_view(), name="authors"),
    path("authors/<str:author_uuid>", AuthorView.as_view(), name="author"),
]
