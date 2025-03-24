"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, URLPattern, URLResolver
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular import views as spectacular_views

urlpatterns: list[URLPattern | URLResolver] = [
    path("", RedirectView.as_view(url="stream")),
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
    path("", include("user_management.urls")),
    path("", include("likes.urls")),
    path("", include("comments.urls")),


    # Schema views
    path("api/schema/",
         spectacular_views.SpectacularAPIView.as_view(),
         name="schema"),
    path("api/schema/swagger-ui/",
         spectacular_views.SpectacularSwaggerView.as_view(url_name="schema"),
         name="swagger-ui"),
    path("api/schema/redoc/",
         spectacular_views.SpectacularRedocView.as_view(url_name="schema"),
         name="redoc"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
