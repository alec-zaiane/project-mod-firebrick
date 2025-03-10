from __future__ import annotations

from typing import Optional

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from socialnetwork.utils.user_control_decorator import user_controller
from socialnetwork import serializers
from socialnetwork import models

from drf_spectacular.utils import extend_schema




def get_unauthenticated_response_api() -> Response:
    return Response(status=401)


@extend_schema(
    deprecated=True,
)
@api_view(["POST"])
@user_controller(must_be_logged_in=True, must_be_author=True)
def api_textpost_create(request: Request, viewer: Optional[models.LocalAuthor]) -> Response:
    """Create a text based post
    Will serve a redirect if unauthorized
    Expects JSON
        {
            "content":<post content>:str
            "visibility_type":<either 'PU' for public, 'FO' for Friends Only, 'UN' for unlisted>:str
            "post_type":<either 'PT' for plaintext, or 'MD' for markdown>:str
        }
    returns JSON on success (code 201)
        {
            "detail": "post created"
            "post": {
                <post details>
            }
        }
    returns JSON on failure (code 400)
        {
            "error": "creation error"
            "post": {
                <errors for each field>
            }
        }
    """
    if viewer is None:  # shouldn't be possible, needed for mypy
        return get_unauthenticated_response_api()

    data = request.data.copy()
    data["base_author"] = viewer.uuid

    serializer = serializers.PostTextBasedSerializer(data=data)

    # save it all
    if serializer.is_valid():
        post = serializer.save()
        post.send_to_required_private_inboxes()
        return Response({"detail": "post created", "post": serializer.data}, status=201)
    else:
        return Response({"error": "creation error", "post": serializer.errors}, status=400)


@extend_schema(
    deprecated=True,
)
@api_view(["PUT", "PATCH"])
@user_controller(must_be_logged_in=True, must_be_author=True)
def api_author_update(request: Request, target_author_uuid: str, viewer: Optional[models.LocalAuthor] = None) -> Response:
    """Update an author's information, **author kwarg is not the target author, but the viewer author**
    Only an admin or the author themselves can update their information"

    Will serve a redirect if unauthorized
    expects JSON
        {
            "username":<updated username>:str (optional)
            "first_name":<updated first name>:str (optional)
            "last_name":<updated last name>:str (optional)
            "email":<updated email>:str (optional)
        }

    will return a 404 on not found
    returns JSON on failure (code 403)
        {
            "error": "You do not have permission to update this author"
        }
    returns JSON on failure (code 400)
        {
            "error": "author update error"
            "author": {
                <errors for each field>
            }
        }

    returns JSON on success (code 200)
        {
            "detail": "author updated"
            "author": {
                <updated author fields>
            }
        }
    """
    target_author = get_object_or_404(
        models.LocalAuthor, uuid=target_author_uuid)
    if viewer != target_author and not request.user.is_superuser:
        return Response({"error": "You do not have permission to update this author"}, status=403)
    serializer = serializers.LocalAuthorSerializer(
        target_author, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(target_author, request.data.copy())
        return Response({"detail": "author updated", "author": serializer.data}, 200)
    return Response({"error": "author update error", "author": serializer.errors}, status=400)


@extend_schema(
    deprecated=True,
)
@api_view(["POST"])
@user_controller(must_be_logged_in=True, must_be_author=True)
def api_post_delete(request: Request, viewer: Optional[models.LocalAuthor], post_uuid: str) -> Response:
    """Delete a post
    Will serve an unauthorized response if unauthorized

    Expects no body
    Will serve a 404 on not found

    returns JSON on error (code 403)
        {
            "error": <error>:str
        }

    returns JSON on success (code 200)
        {
            "success": <success>:str
        }
    """
    post = get_object_or_404(models.PostTextBased, uuid=post_uuid)

    # Only the post's owner can delete
    if post.author != viewer:
        return Response({"error": "You must be the author of this post to delete it"}, 403)

    # Perform the soft delete
    # this is ssetting is_deleted to = True which is added field to author_posts above
    post.delete()
    return Response({"detail": "Post deleted successfully"}, 200)


@extend_schema(
    deprecated=True,
)
@api_view(["POST"])
@user_controller(must_be_logged_in=True, must_be_author=True)
def api_textpost_update(request: Request, viewer: Optional[models.LocalAuthor], post_uuid: str) -> Response:
    """Modify a post
    Will serve an unauthorized response if unauthorized

    Expects JSON
        {
            "content":<post content>:str (optional)
            "visibility_type":<either 'PU' for public, 'FO' for Friends Only, 'UN' for unlisted>:str (optional)
            "post_type":<either 'PT' for plaintext, or 'MD' for markdown>:str (optional)
        }
    Will serve a 404 on not found

    returns JSON on error (code 403)
        {
            "error": <error>:str
            "post": {
                <errors for each field>
            }
        }

    returns JSON on success (code 200)
        {
            "detail": "post updated"
            "post": {
                <updated post details>
            }
        }
    """
    post = get_object_or_404(models.PostTextBased, uuid=post_uuid)
    if post.author != viewer:
        return Response({"error": "You must be the author of this post to modify it"}, 403)
    serializer = serializers.PostTextBasedSerializer(
        post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(post, request.data.copy())
        return Response({"detail": "post updated", "post": serializer.data}, 200)
    return Response({"error": "post update error", "post": serializer.errors}, 403)


@api_view(["POST"])
@user_controller(must_be_logged_in=True, must_be_author=True)
def api_imagepost_create(request: Request, viewer: Optional[models.LocalAuthor]) -> Response:
    """
    Create an image-based post and return the markdown link.

    Expects:
    - A multipart/form-data request containing:
        - `image`: File
        - `visibility_type`: PU (Public), FO (Friends Only), UN (Unlisted)
    Returns:
    - 201 on success with post data + Markdown URL.
    - 400 on failure with error messages.
    """
    if viewer is None:
        return get_unauthenticated_response_api()

    data = request.data.copy()
    data["base_author"] = viewer.uuid  # Assign author to post

    serializer = serializers.PostMediaBasedSerializer(data=data)

    if serializer.is_valid():
        post = serializer.save()
        post.send_to_required_private_inboxes()
        
        # Generate Markdown format
        markdown_url = f"![{post.image.name}]({request.build_absolute_uri(post.image.url)})"
        
        return Response(
            {
                "detail": "Image post created",
                "post": serializer.data,
                "markdown": markdown_url  # Return the Markdown URL
            }, 
            status=201
        )
    else:
        return Response({"error": "creation error", "post": serializer.errors}, status=400)
