from __future__ import annotations
from typing import Optional, Any
import abc

from rest_framework import views
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from likes.serializers import LikeSerializer
from likes.viewsets import LikeViewSet

from comments.serializers import CommentSerializer
from comments.viewsets import CommentViewSet

from posts.models import Post

from user_management.serializers import FollowRequestSerializer
from user_management.viewsets import FollowRequestViewSet
from user_management.models import Author

from core.utils.request_viewer import get_request_node
from core.utils.redirects import API_UNAUTHORIZED

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer

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

    def _post_to_viewset(self, request: Request, viewset_instance: ModelViewSet[Any]) -> Response:
        """Post to a viewset with the request object *calls the `create` method*"""
        viewset_instance.setup(request)
        viewset_instance.initial(request)
        return viewset_instance.create(request)


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
    def post(self, request: Request, target_author_fqid: str) -> Response:
        """Send an inbox item to this author's inbox"""
        type = request.data.get("type")
        if type is None:
            return Response({"error": "missing 'type' field under inbox item"}, 400)

        # make sure the author FQID is valid
        if not target_author_fqid:
            return Response({"error": "missing 'target_author_fqid' field"}, 400)
        target_author = Author.local_authors.find_by_encoded_fqid(target_author_fqid)
        if target_author is None:
            return Response({"error": "Author not found", "fqid": target_author_fqid}, 404)

        handler = self._find_handler_for_type(type)
        if handler is not None:
            # if not hasattr(request, 'resolver_match') or request.resolver_match is None:
            #     stub = ResolverMatchStub()
            #     setattr(request, 'resolver_match', stub)
            # resolver_match = getattr(request, 'resolver_match')
            # resolver_match.kwargs['target_author_fqid'] = target_author_fqid
            return handler.post(request, target_author)
        return Response({"error": "invalid 'type' field under inbox item",
                         "type": type}, 400)


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
        return self._post_to_viewset(request, LikeViewSet())


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
        return self._post_to_viewset(request, CommentViewSet())


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

        return self._post_to_viewset(request, FollowRequestViewSet())


register_inbox_handler(FollowRequestInboxHandler())
