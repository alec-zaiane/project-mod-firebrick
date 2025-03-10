from django.urls import path
from api.views import *

from django.views import View

from drf_spectacular import views as spectacular_views

from api.views.search import AuthorSearchView

from api.views.follow import (
    SendFollowRequestView,
    ApproveFollowRequestView,
    DenyFollowRequestView,
    UnfollowView,
    ListFollowRequestsView,
    ListFollowersView,
    ListFollowingView,
    ListFriendsView,
)

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

    # Inbox API
    path("authors/<str:author_uuid>/inbox",
         InboxView.as_view(),
         name="inbox"),

    # Authors / Single Author API
    path("authors",
         AuthorsView.as_view(),
         name="authors"),
    path("authors/<str:author_uuid_or_fqid>",
         AuthorView.as_view(),
         name="author"),

     # Followers API
     path("authors/<str:author_uuid>/followers",
          FollowersView.as_view(),
          name="followers"),
     path("authors/<str:author_uuid>/followers/<str:foreign_author_fqid>",
          FollowersSpecificView.as_view(),
          name="followers_specific"),

     # Follow Request API
     # handled by InboxView already

     # Posts API
     path("authors/<str:author_uuid>/posts/<str:post_uuid>",
          PostAuthorSpecificView.as_view(),
          name="post_author_specific"),
     path("posts/<str:post_fqid>",
          PostByFqidView.as_view(),
          name="post_by_fqid"),
     path("authors/<str:author_uuid>/posts",
          PostCreationView.as_view(),
          name="post_creation"),

     # Image Posts API
     path("authors/<str:author_uuid>/posts/<str:post_uuid>/image",
          ImagePostAuthorSpecificView.as_view(),
          name="image_post_author_specific"),
     path("posts/<str:post_fqid>/image",
          ImagePostByFqidView.as_view(),
          name="image_post_by_fqid"),

     # Comments API
     path("authors/<str:author_uuid>/posts/<str:post_uuid>/comments",
          CommentsSerialView.as_view(),
          name="comments_serial"),
     path("posts/<str:post_fqid>/comments",
          CommentsFqidView.as_view(),
          name="comments_fqid"),
     #     Technically this should be author/.../post/... in the class spec but i'm guessing that's a typo as it's `posts` everywhere else
     path("authors/<str:author_uuid>/posts/<str:post_uuid>/comment/<str:comment_uuid_or_fqid>",
          CommentsRemoteFqidView.as_view(),
          name="comments_fqid_on_local_post"),

     # Commented API
     path("authors/<str:author_uuid_or_fqid>/commented",
          CommentedAuthorView.as_view(),
          name="commented_author"),
     path("authors/<str:author_uuid>/commented/<str:comment_uuid>",
          CommentedBySerialView.as_view(),
          name="commented_serial"),
     path("comments/<str:comment_fqid>",
          CommentedFqidView.as_view(),
          name="commented_fqid"),

     # Likes API
     path("authors/<str:author_uuid>/posts/<str:post_uuid>/likes",
          LikesOnPostBySerialView.as_view(),
          name="likes_on_post_by_serial"),
     path("posts/<str:post_fqid>/likes",
          LikesOnPostByFqidView.as_view(),
          name="likes_on_post_by_fqid"),
     path("authors/<str:author_uuid>/posts/<str:post_uuid>/comments/<str:comment_fqid>/likes",
          LikesOnCommentView.as_view(),
          name="likes_on_comment"),
     path("posts/<str:post_uuid>/internal_likes",
          LikePostInternalView.as_view(),
          name="like_post_internal"),

     # Liked API
     path("authors/<str:author_uuid_or_fqid>/liked",
          LikedByAuthorView.as_view(),
          name="liked_author"),

     path("authors/<str:author_uuid_or_fqid>/liked/<str:like_uuid>",
          LikedByAuthorSpecificLikeView.as_view(),
          name="liked_author_specific_like"),

     path("liked/<str:like_fqid>",
          LikedSpecificLikeView.as_view(),
          name="liked_specific_like"),

     path("follow/request/<str:target_id>/",
          SendFollowRequestView.as_view(), name="send_follow_request"),
     path("follow/request/<uuid:request_id>/approve/",
          ApproveFollowRequestView.as_view(), name="approve_follow_request"),
     path("follow/request/<uuid:request_id>/deny/",
          DenyFollowRequestView.as_view(), name="deny_follow_request"),
     path("follow/<str:target_id>/unfollow/",
          UnfollowView.as_view(), name="unfollow"),
     path("follow/requests/", ListFollowRequestsView.as_view(),
          name="list_follow_requests"),
     path("follow/followers/", ListFollowersView.as_view(), name="list_followers"),
     path("follow/following/", ListFollowingView.as_view(), name="list_following"),
     path("follow/friends/", ListFriendsView.as_view(), name="list_friends"),

     path("search/authors/", AuthorSearchView.as_view(), name="author_search"),
]
