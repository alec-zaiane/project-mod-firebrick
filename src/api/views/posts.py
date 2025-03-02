from typing import Optional

from itertools import chain

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from socialnetwork.utils.user_control_decorator import user_controller, user_control
from socialnetwork import models
from api import serializers

# ============= Posts =============
"""
Posts API:
URL: `://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}`
- GET [local, remote] get the public post whose serial is POST_SERIAL
    - friends-only posts: must be authenticated
- DELETE [local] remove a post
    - local posts: must be authenticated locally as the author
- PUT [local] update a post
    - local posts: must be authenticated locally as the author

URL: `://service/api/posts/{POST_FQID}`
- GET [local] get the public post whose URL is POST_FQID
    - friends-only posts: must be authenticated

Creation URL `://service/api/authors/{AUTHOR_SERIAL}/posts/`
- GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
    - Not authenticated: only public posts.
    - Authenticated locally as author: all posts.
    - Authenticated locally as follower of author: public + unlisted posts.
    - Authenticated locally as friend of author: all posts.
    - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
- POST [local] create a new post but generate a new ID
    - Authenticated locally as author

Be aware that Posts can be images that need base64 decoding.
    - posts can also hyperlink to images that are public
Uses the same format as the post object
For [local] service, fields included may differ. For example, when first creating the post, there's no reason to have likes, comments, etc. because it doesn't exist yet. Be sure to document this!
"""


class PostAuthorSpecificView(views.APIView):
    """
    URL: `://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}`
    - GET [local, remote] get the public post whose serial is POST_SERIAL
        - friends-only posts: must be authenticated
    - DELETE [local] remove a post
        - local posts: must be authenticated locally as the author
    - PUT [local] update a post
        - local posts: must be authenticated locally as the author
    """

    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, post_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def delete(self, request: Request, author_uuid: str, post_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def put(self, request: Request, author_uuid: str, post_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        raise NotImplementedError("TODO")


class PostByFqidView(views.APIView):
    """
    URL: `://service/api/posts/{POST_FQID}`
    - GET [local] get the public post whose URL is POST_FQID
        - friends-only posts: must be authenticated
    """
    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, post_fqid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
        raise NotImplementedError("TODO")


class PostCreationView(views.APIView):
    """
    Creation URL `://service/api/authors/{AUTHOR_SERIAL}/posts/`
    - GET [local, remote] get the recent posts from author AUTHOR_SERIAL (paginated)
        - Not authenticated: only public posts.
        - Authenticated locally as author: all posts.
        - Authenticated locally as follower of author: public + unlisted posts.
        - Authenticated locally as friend of author: all posts.
        - Authenticated as remote node: This probably should not happen. Remember, the way remote node becomes aware of local posts is by local node pushing those posts to inbox, not by remote node pulling.
    - POST [local] create a new post but generate a new ID
        - Authenticated locally as author
    """
    @extend_schema(

    )
    @method_decorator(user_controller())
    def get(self, request: Request, author_uuid: str, viewer: Optional[models.LocalAuthor]) -> Response:
        raise NotImplementedError("TODO")

    @extend_schema(

    )
    @method_decorator(user_controller())
    def post(self, request: Request, author_uuid: str, viewer: Optional[models.LocalAuthor]) -> Response:
        raise NotImplementedError("TODO")


# ============= Image Posts =============
"""
Image Posts are just posts that are images. But they are encoded as base64 data. You can inline an image post using a data URL, or you can use this shortcut to get the image if authenticated to see it.

URL: `://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image`
- GET [local, remote] get the public post converted to binary as an image
- return 404 if not an image

URL: `://service/api/posts/{POST_FQID}/image`
- GET [local, remote] get the public post converted to binary as an image
- return 404 if not an image

This end point decodes image posts as images. This allows the use of image tags in Markdown.
You can use this to proxy or cache images.
"""


class ImagePostAuthorSpecificView(views.APIView):
    """
    URL: `://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image`
    - GET [local, remote] get the public post converted to binary as an image
    - return 404 if not an image
    """
    pass  # TODO


class ImagePostByFqidView(views.APIView):
    """
    URL: `://service/api/posts/{POST_FQID}/image`
    - GET [local, remote] get the public post converted to binary as an image
    - return 404 if not an image
    """
    pass  # TODO
