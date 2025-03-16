from rest_framework import routers
from django.urls import URLPattern, URLResolver
from django.contrib.auth import views as auth_views
from django.urls import path
from user_management.forms import LoginForm

from user_management.views import join_view
from user_management.viewsets import AuthorViewSet

app_name = "user_management"
urlpatterns: list[URLPattern | URLResolver] = [

]

router = routers.SimpleRouter()
# creates names: author-list, author-detail, author-create, author-update, author-delete
router.register(r"authors", AuthorViewSet)

urlpatterns += router.urls

urlpatterns.append(
    path('login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm), name='login')
)

urlpatterns.append(
    path('join/',
         join_view, name='join')
)
