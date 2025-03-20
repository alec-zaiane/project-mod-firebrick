
from __future__ import annotations
from typing import Optional, Any
import abc

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from likes.serializers import LikeSerializer

from core.utils.request_viewer import get_request_viewer


from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiExample, PolymorphicProxySerializer

# ======================================================================================
# Inbox handling
# A combined view for all calls to `://service/api/authors/{AUTHOR_SERIAL}/inbox`

# list of InboxHandlers that the InboxView will go through, call register_inbox_handler to register to it
_INBOX_HANDLERS: set[InboxHandler] = set()


def register_inbox_handler(handler: InboxHandler) -> None:
    _INBOX_HANDLERS.add(handler)


def _get_serializer_map() -> dict[str, Serializer[Any] | type[Serializer[Any]]]:
    return {handler.handlable_type: handler.serializer for handler in _INBOX_HANDLERS}


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
    def post(self, request: Request) -> Response:
        ...


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
        description="Send an inbox item to this author's inbox",
        request=PolymorphicProxySerializer(
            component_name="InboxItem",
            serializers=_get_serializer_map,
            resource_type_field_name="type"
        ),
        responses={200: OpenApiResponse(description="Success, inbox item sent"),
                   400: OpenApiResponse(description="Bad request")},
    )
    def post(self, request: Request, target_author_uuid: str) -> Response:
        """Send an inbox item to this author's inbox"""
        type = request.data.get("type")
        if type is None:
            return Response({"error": "missing 'type' field under inbox item"}, 400)
        handler = self._find_handler_for_type(type)
        if handler is not None:
            return handler.post(request)
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
        return LikeSerializer

    def post(self, request: Request) -> Response:
        serializer = LikeSerializer(data=request.data)
        viewer = get_request_viewer(request)
        if viewer is None:
            return Response("User must be authenticated", status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            # double check that the author has access to the target object
            like_target = serializer.get_target()
            if not like_target.check_can_be_seen_by(viewer):
                return Response("User does not have access to target object", status.HTTP_403_FORBIDDEN)
            like = serializer.create(serializer.validated_data)
            return Response({
                "detail": "Like Created",
                "like": serializer.to_representation(like)
            }, status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "Invalid Like",
                "like": serializer.errors
            }, status.HTTP_400_BAD_REQUEST)


register_inbox_handler(LikesInboxHandler())
