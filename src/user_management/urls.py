from rest_framework import routers
from django.urls import URLPattern, URLResolver
from django.contrib.auth import views as auth_views
from django.urls import path
from user_management.forms import LoginForm


from user_management.views import AuthorFollowInfoView, AuthorFollowRequests, AuthorModifyView, AuthorView, FollowRequestByViewer, JoinView, AuthorSearchAPIView
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
    path("authors/<uuid:target_author_uuid>/following",
         AuthorFollowInfoView.as_view(follow_type="following"),
         name="author_following"),
    path("authors/<uuid:target_author_uuid>/followers",
         AuthorFollowInfoView.as_view(follow_type="followers"),
         name="author_followers"),
    path("authors/<uuid:target_author_uuid>/friends",
         AuthorFollowInfoView.as_view(follow_type="friends"),
         name="author_friends"),


    path("follow-requests",
         AuthorFollowRequests.as_view(),
         name="follow_requests"),



    path("api/authors/<uuid:target_author_uuid>/inbox",
         InboxView.as_view(),
         name="node2node_inbox"
         ),

    path("api/authors/search/",
         AuthorSearchAPIView.as_view(),
         name="author_search"),

    path("api/follow-requests/<str:target_fqid>/request-follow",
         FollowRequestByViewer.as_view(),
         name="follow_request"),
]

router = routers.SimpleRouter()
# creates names: author-list, author-detail, author-create, author-update, author-delete
router.register(r"api/authors", AuthorViewSet, basename="node2node_authors")
router.register(r"api/follow-requests", FollowRequestViewSet, basename="node2node_follow_requests")

urlpatterns += router.urls

# suggested by copilot: register explicit approve/deny endpoints because the regex is matching the / as part of the FQID
# for some reason, percent decoding is done before the regex is matched, making all FQIDs either break themselves, or break any trailing URL
urlpatterns += [
    # For Authors:
    path("api/authors/<uuid:uuid>/unfollow",
         AuthorViewSet.as_view({"post": "unfollow"}),
         name="node2node_authors-unfollow"),

    # For Follow requests:
    path("api/follow-requests/<uuid:uuid>/approve",
         FollowRequestViewSet.as_view({"post": "approve_follow_request"}),
         name="node2node_follow_requests-approve"),
    path("api/follow-requests/<uuid:uuid>/deny",
         FollowRequestViewSet.as_view({"post": "deny_follow_request"}),
         name="node2node_follow_requests-deny"),
    path("api/follow-requests/pending-count",
         FollowRequestViewSet.as_view({"get": "pending_count"}),
         name="node2node_follow_requests-pending-count"),
]
