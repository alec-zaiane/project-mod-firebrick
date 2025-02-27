from __future__ import annotations

from typing import Optional

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from socialnetwork.utils.user_control_decorator import user_control
from socialnetwork import serializers
from socialnetwork import models


@api_view(["POST"])
@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def api_create_text_post(request: Request, author: models.LocalAuthor) -> Response:
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
    data = request.data.copy()
    data["base_author"] = author.uuid

    serializer = serializers.PostTextBasedSerializer(data=data)

    # save it all
    if serializer.is_valid():
        post = serializer.save()
        post.send_to_required_private_inboxes()
        return Response({"detail": "post created", "post": serializer.data}, status=201)
    else:
        return Response({"error": "creation error", "post": serializer.errors}, status=400)


@api_view(["PUT", "PATCH"])
@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=True)
def api_author_update(request: Request, target_author_uuid: str, author: Optional[models.LocalAuthor] = None) -> Response:
    """Update an author's information, **author kwarg is not the target author, but the viewer author**
    Only an admin or the author themselves can update their information"

    Will serve a redirect if unauthorized
    expects JSON
        {
            "following":<list of author uuids>:list[str] (optional)
            "username":<updated username>:str (optional)
            "first_name":<updated first name>:str (optional)
            "last_name":<updated last name>:str (optional)
            "email":<updated email>:str (optional)
        }
    Alternative JSON
        {
            "user" {
                "username":<updated username>:str (optional)
                "first_name":<updated first name>:str (optional)
                "last_name":<updated last name>:str (optional)
                "email":<updated email>:str (optional)
            }
            "following":<list of author uuids>:list[str] (optional)
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
    if author != target_author and not request.user.is_superuser:
        return Response({"error": "You do not have permission to update this author"}, status=403)
    serializer = serializers.LocalAuthorSerializer(
        target_author, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(target_author, request.data.copy())
        return Response({"detail": "author updated", "author": serializer.data}, 200)
    return Response({"error": "author update error", "author": serializer.errors}, status=400)


@api_view(["POST"])
@user_control(can_be_author=True, can_be_logged_out=False, can_be_superuser=False)
def api_post_delete(request: Request, author: models.LocalAuthor, post_uuid: str) -> Response:
    """Delete a post
    Will serve a redirect if unauthorized

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
    if post.author != author:
        return Response({"error": "You must be the author of this post to delete it"}, 403)

    # Perform the soft delete
    # this is ssetting is_deleted to = True which is added field to author_posts above
    post.delete()
    return Response({"detail": "Post deleted successfully"}, 200)
