from rest_framework import routers
from django.urls import URLPattern, URLResolver
from django.contrib.auth import views as auth_views
from django.urls import path
from user_management.forms import LoginForm


from user_management.views import AuthorModifyView, AuthorView, JoinView
from user_management.viewsets import AuthorViewSet, FollowRequestViewSet
from user_management.views_api import InboxView

app_name = "user_management"
urlpatterns: list[URLPattern | URLResolver] = [
    path('login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),
    path('join/',
         JoinView.as_view(),
         name='join'),
    path("authors/<uuid:target_author_uuid>/",
         AuthorView.as_view(),
         name="author_profile"),
    path("authors/<uuid:target_author_uuid>/modify/",
         AuthorModifyView.as_view(),
         name="author_modify"),



    path("api/authors/<uuid:target_author_uuid>/inbox",
         InboxView.as_view(),
         name="node2node_inbox"
         )
]

router = routers.SimpleRouter()
# creates names: author-list, author-detail, author-create, author-update, author-delete
router.register(r"api/authors", AuthorViewSet)
router.register(r"api/follow-requests", FollowRequestViewSet, basename="follow-requests")

urlpatterns += router.urls
