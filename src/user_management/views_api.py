from __future__ import annotations
from typing import Optional, Any, Literal
import abc

from rest_framework import views
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from likes.serializers import LikeSerializer
from likes.viewsets import LikeViewSet

from comments.models import Comment
from comments.serializers import CommentSerializer
from comments.viewsets import CommentViewSet

from posts.models import Post
from posts.serializers import PostSerializer
from posts.viewsets import PostViewSet

from user_management.serializers import FollowRequestSerializer, AuthorSerializer
from user_management.viewsets import FollowRequestViewSet
from user_management.models import Author, FollowRequest

from core.utils.request_viewer import get_request_node, get_request_viewer
from core.utils.redirects import API_UNAUTHORIZED, API_FORBIDDEN

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer

from uuid import UUID

# ======================================================================================
# Inbox handling
# A combined view for all calls to `://service/api/authors/{AUTHOR_SERIAL}/inbox`

# list of InboxHandlers that the InboxView will go through, call register_inbox_handler to register to it
_INBOX_HANDLERS: set[InboxHandler] = set()


def register_inbox_handler(handler: InboxHandler) -> None:
    _INBOX_HANDLERS.add(handler)


def _get_serializer_map() -> dict[str, Serializer[Any] | type[Serializer[Any]]]:
    return {handler.handlable_type: handler.serializer for handler in _INBOX_HANDLERS}


class ResolverMatchStub:
    """A stub class to mimic Django's ResolverMatch for type checking purposes"""

    def __init__(self) -> None:
        self.kwargs: dict[str, Any] = {}


class InboxHandler(abc.ABC):
    """InboxHandler class that handles a specific type of inbox item
    When calling __init__, pass in a list of types that this handler can handle
    """

    def __init__(self, handlable_types: str):
        self.handlable_type: str = handlable_types

    @property
    @abc.abstractmethod
    def serializer(self) -> type[Serializer[Any]]:
        """Returns the *type* of serializer that should be used for this handler"""
        ...

    def can_handle(self, type: str) -> bool:
        return type == self.handlable_type

    @abc.abstractmethod
    def post(self, request: Request, target_author: Author) -> Response:
        """Process the inbox item for the inbox of the target author, return a response"""
        ...

    @abc.abstractmethod
    def put(self, request: Request, target_author: Author) -> Response:
        ...

    @abc.abstractmethod
    def delete(self, request: Request, target_author: Author) -> Response:
        ...

    # def _post_to_viewset(self, request: Request, viewset_instance: ModelViewSet[Any]) -> Response:
    #     """Post to a viewset with the request object *calls the `create` method*"""
    #     viewset_instance.setup(request)
    #     viewset_instance.initial(request)
    #     return viewset_instance.create(request)

    def _request_to_viewset(self, request: Request, viewset_instance: ModelViewSet[Any], method: str = "POST") -> Response:
        """Make a request to a viewset with the specified method (POST/PUT/DELETE)"""
        viewset_instance.setup(request)
        viewset_instance.initial(request)

        match method.upper():
            case "POST":
                return viewset_instance.create(request)
            case "PUT":
                return viewset_instance.update(request)
            case "DELETE":
                return viewset_instance.destroy(request)
            case _:
                return Response({"error": f"Unsupported method {method}"}, status=405)


class InboxView(views.APIView):
    """Inbox view that handles all incoming inbox events:
    - Follow requests
    - Incoming Comments
    - Incoming Likes
    - etc...

    All inbox calls are POSTs with "type": <something> fields
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self.inbox_handlers = _INBOX_HANDLERS
        super().__init__(*args, **kwargs)

    def _handle_method(self, request: Request, target_author_uuid: UUID, method: str) -> Response:
        type = request.data.get("type")
        if type is None:
            return Response({"error": "missing 'type' field under inbox item"}, 400)

        target_author = Author.local_authors.find_by_uuid(target_author_uuid)
        if target_author is None:
            return Response({"error": "Author not found", "uuid": target_author_uuid}, 404)

        handler = self._find_handler_for_type(type)
        if handler is None:
            return Response({"error": f"invalid 'type': {type}"}, 400)

        match method.upper():
            case "POST":
                return handler.post(request, target_author)
            case "PUT":
                return handler.put(request, target_author)
            case "DELETE":
                return handler.delete(request, target_author)
            case _:
                return Response({"error": f"Unsupported method {method}"}, 405)

    def _find_handler_for_type(self, type: str) -> Optional[InboxHandler]:
        for handler in self.inbox_handlers:
            if handler.can_handle(type):
                return handler
        return None

    @extend_schema(
        operation_id="send_to_inbox",
        summary="Send to Author's Inbox",
        description="""Send an item to an author's inbox. Supported types:
    - Like objects
    - Comment objects""",
        parameters=[
            OpenApiParameter(
                name="target_author_fqid",
                location=OpenApiParameter.PATH,
                description="FQID of the target author",
                required=True,
                type=str,
            )
        ],
        request=PolymorphicProxySerializer(
            component_name="InboxItem",
            serializers=_get_serializer_map,
            resource_type_field_name="type",
        ),
        responses={
            200: OpenApiResponse(description="Success, inbox item sent"),
            400: OpenApiResponse(
                description="Bad request",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "missing 'type' field under inbox item",
                        }
                    },
                },
            ),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to send to this inbox"),
            404: OpenApiResponse(description="Author not found"),
        },
        tags=["Inbox"],
    )
    def post(self, request: Request, target_author_uuid: UUID) -> Response:
        return self._handle_method(request, target_author_uuid, "POST")

    def put(self, request: Request, target_author_uuid: UUID) -> Response:
        return self._handle_method(request, target_author_uuid, "PUT")

    def delete(self, request: Request, target_author_uuid: UUID) -> Response:
        return self._handle_method(request, target_author_uuid, "DELETE")

    # def post(self, request: Request, target_author_uuid: UUID) -> Response:
    #     """Send an inbox item to this author's inbox"""
    #     type = request.data.get("type")
    #     if type is None:
    #         return Response({"error": "missing 'type' field under inbox item"}, 400)

    #     # make sure the author FQID is valid
    #     if not target_author_uuid:
    #         return Response({"error": "missing 'target_author_uuid' field"}, 400)
    #     target_author = Author.local_authors.find_by_uuid(target_author_uuid)
    #     if target_author is None:
    #         return Response({"error": "Author not found", "uuid": target_author_uuid}, 404)

    #     handler = self._find_handler_for_type(type)
    #     if handler is not None:
    #         # if not hasattr(request, 'resolver_match') or request.resolver_match is None:
    #         #     stub = ResolverMatchStub()
    #         #     setattr(request, 'resolver_match', stub)
    #         # resolver_match = getattr(request, 'resolver_match')
    #         # resolver_match.kwargs['target_author_fqid'] = target_author_fqid
    #         return handler.post(request, target_author)
    #     return Response({"error": "invalid 'type' field under inbox item",
    #                      "type": type}, 400)


class LikesInboxHandler(InboxHandler):
    """
    - URL:`://service/api/authors/{AUTHOR_SERIAL}/inbox`
        - `POST`[remote]: send a like object to`AUTHOR_SERIAL`
        - Body is [like object]
    """

    def __init__(self) -> None:
        super().__init__("like")

    @property
    def serializer(self) -> type[LikeSerializer]:
        return LikeSerializer  # pragma: no cover

    def post(self, request: Request, target_author: Author) -> Response:
        # make sure the request's owner has access to the post
        if get_request_node(request) is None:  # if they are a node, we're good
            # otherwise, make sure the author can see the targeted post
            viewer = get_request_viewer(request)
            if viewer is None:
                return API_UNAUTHORIZED()
            post_id = request.data.get("object")
            if post_id is None:
                return Response({"error": "missing 'object' field"}, 400)
            post = Post.visible_posts.find_by_fqid(post_id)
            comment = Comment.objects.find_by_fqid(post_id)
            if post is None and comment is None:
                return Response({"error": "`object` not found", "fqid": post_id}, 404)
            if comment is not None:
                post = comment.post
            if post is None:
                # this shouldn't ever happen, just a sanity check
                return Response({"error": "Post not found", "fqid": post_id}, 404)
            if not post.check_can_be_seen_by(viewer):
                return API_FORBIDDEN()

        # return self._post_to_viewset(request, LikeViewSet())
        return self._request_to_viewset(request, LikeViewSet(), method="POST")

    def put(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "PUT not supported for likes"}, status=405)

    def delete(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "DELETE not supported for likes"}, status=405)


register_inbox_handler(LikesInboxHandler())


class CommentInboxHandler(InboxHandler):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
        - POST [remote]: comment on a post by AUTHOR_SERIAL
        - Body is a comment object
    """

    def __init__(self) -> None:
        super().__init__("comment")

    @property
    def serializer(self) -> type[CommentSerializer]:
        return CommentSerializer  # pragma: no cover

    def post(self, request: Request, target_author: Author) -> Response:
        # make sure the request's owner has access to the post
        if get_request_node(request) is None:  # if they are a node, we're good
            # otherwise, make sure the author can see the targeted post
            viewer = get_request_viewer(request)
            if viewer is None:
                return API_UNAUTHORIZED()
            post_id = request.data.get("post")
            if post_id is None:
                return Response({"error": "missing 'post' field"}, 400)
            post = Post.visible_posts.find_by_fqid(post_id)
            if post is None:
                return Response({"error": "Post not found", "fqid": post_id}, 404)
            if not post.check_can_be_seen_by(viewer):
                return API_FORBIDDEN()

        return self._request_to_viewset(request, CommentViewSet(), method="POST")

    def put(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "PUT not supported for comments"}, status=405)

    def delete(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "DELETE not supported for comments"}, status=405)


register_inbox_handler(CommentInboxHandler())


class FollowRequestInboxHandler(InboxHandler):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
        - POST [remote]: follow request to AUTHOR_SERIAL
        - Body is a follow request object
    """

    def __init__(self) -> None:
        super().__init__("follow")

    @property
    def serializer(self) -> type[FollowRequestSerializer]:
        return FollowRequestSerializer  # pragma: no cover

    def post(self, request: Request, target_author: Author) -> Response:
        request_object: dict[str, Any] = request.data.get('object', {})
        request_object_id = request_object.get('id')

        if not request_object_id or request_object_id != target_author.fqid:
            return Response(
                {"error": "Follow request target doesn't match the inbox owner"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return self._request_to_viewset(request, FollowRequestViewSet(), method="POST")

    def put(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "PUT not supported for follow requests"}, status=405)

    def delete(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "DELETE not supported for follow requests"}, status=405)


register_inbox_handler(FollowRequestInboxHandler())


class PostInboxHandler(InboxHandler):
    """
    - URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
        - POST [remote]: post to AUTHOR_SERIAL
        - Body is a post object
    """

    def __init__(self) -> None:
        super().__init__("post")

    @property
    def serializer(self) -> type[PostSerializer]:
        return PostSerializer  # pragma: no cover

    def post(self, request: Request, target_author: Author) -> Response:
        # since a post is being created, we don't need to check if the author can see it
        # return self._post_to_viewset(request, PostViewSet())
        return self._request_to_viewset(request, PostViewSet(), method="POST")

    def put(self, request: Request, target_author: Author) -> Response:
        return self._request_to_viewset(request, PostViewSet(), method="PUT")

    def delete(self, request: Request, target_author: Author) -> Response:
        return self._request_to_viewset(request, PostViewSet(), method="DELETE")


register_inbox_handler(PostInboxHandler())


class FollowDecisionInboxHandler(InboxHandler):
    """
    Receive a follow-decision inbox object to approve/deny a follow request
    example:
    ```
    {
        "type": "follow-decision",
        "decision": "true",
        "actor": {
            "type": "author",
            "id": "http://370ea.yeg.rac.sh/api/authors/1",
            "host": "http://370ea.yeg.rac.sh/api/",
            "displayName": "blue",
            "github": "None",
            "profileImage": "None",
            "page": "http://370ea.yeg.rac.sh/authors/blue"
        },
        "object": {
            "type": "author",
            "id": "http://10.2.4.248:8000/api/authors/7",
            "host": "http://10.2.4.248:8000/api/",
            "displayName": "TestProfile1",
            "github": "https://github.com/totallyrealgithub",
            "profileImage": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQXTM-nt34tD8LUQBFbWEKGSdzpbacaHXenmA&s",
            "page": "http://10.2.4.248:8000/authors/7"
        }
    }
    ```
    """

    def __init__(self) -> None:
        super().__init__("follow-decision")

    @property
    def serializer(self) -> None:  # type: ignore # pragma: no cover
        return None

    def post(self, request: Request, target_author: Author) -> Response:
        # TODO this should ideally be a serializer/viewset, not logic here
        json = request.data
        print(json)
        if not json.get("decision"):
            return Response({"error": "missing 'decision' field"}, 400)
        if not json.get("object") or not json.get("actor"):
            return Response({"error": "missing 'object' or 'actor' field"}, 400)
        # actor = AuthorSerializer().to_internal_value(json["actor"])
        actor_serializer = AuthorSerializer(data=json["actor"])
        if not actor_serializer.is_valid():
            return Response({"error": "invalid 'actor' field",
                             "actor": actor_serializer.errors}, 400)
        actor = actor_serializer.get_or_create(json["actor"])
        object_serializer = AuthorSerializer(data=json["object"])
        if not object_serializer.is_valid():
            return Response({"error": "invalid 'object' field",
                             "object": object_serializer.errors}, 400)
        object = object_serializer.get_or_create(json["object"])
        if not actor or not object:
            return Response({"error": "invalid 'object' or 'actor' field"}, 400)
        try:
            decision = bool(json.get("decision"))
        except ValueError:
            return Response({"error": "invalid 'decision' field"}, 400)
        print(decision)
        print(actor)
        print(object)
        if decision:
            # approved
            actor.following.add(object)
            actor.save()

        # remove the follow request object
        existing_follow_request = FollowRequest.objects.filter(
            follower=actor, followee=object).first()
        if existing_follow_request:
            existing_follow_request.delete()
        return Response({"status": "success"}, status=200)

    def put(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "PUT not supported for follow-decision"}, status=405)

    def delete(self, request: Request, target_author: Author) -> Response:
        return Response({"error": "DELETE not supported for follow-decision"}, status=405)


register_inbox_handler(FollowDecisionInboxHandler())
