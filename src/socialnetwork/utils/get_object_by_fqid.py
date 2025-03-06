from typing import Literal, Optional
import uuid

from django.urls import resolve, Resolver404

from socialnetwork.models import Author, Post, Comment, Like, PostDifferentiator
from django.core.exceptions import ObjectDoesNotExist

from project_firebrick.settings import THIS_NODE_URL


def differentiate_id(possible_fqid: str) -> Optional[Literal["FQID", "UUID"]]:
    """
    Differentiate between UUID and FQID, returns None if neither
    """
    try:
        uuid.UUID(possible_fqid)
        return "UUID"
    except ValueError:
        pass
    if possible_fqid.startswith("http://") or possible_fqid.startswith("https://"):
        return "FQID"
    return None


def get_object_by_fqid(fqid: str) -> Author | Post | Comment | Like:
    """
    Get an object by its FQID

    Raises SyntaxError if the FQID is invalid

    Raises NotImplementedError if the object type is not supported

    Raises ObjectDoesNotExist if the object does not exist
    """
    if not fqid.startswith(THIS_NODE_URL):
        # the FQID is not for this node
        # TODO not sure what to do here
        raise NotImplementedError("TODO")
    else:
        # the FQID is for this node
        # start by getting only the path
        fqid = fqid[len(THIS_NODE_URL):]

        try:
            resolved = resolve(fqid)
            if resolved.url_name == "post_author_specific":
                found_post = PostDifferentiator.get_post_by_uuid(
                    resolved.kwargs["post_uuid"])
                # have to use getattr here because author is None if the post is soft-deleted
                if str(getattr(found_post.author, "uuid", None)) == resolved.kwargs["author_uuid"]:
                    return found_post
                else:
                    raise ObjectDoesNotExist("Post does not exist")
            else:
                raise NotImplementedError(
                    f"{resolved.url_name} Is not yet supported in get_object_by_fqid")
        except Resolver404:
            raise SyntaxError(
                "Invalid FQID, are you sure it's an /api/ targeting URL?")
