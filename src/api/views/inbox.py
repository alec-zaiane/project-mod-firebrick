from __future__ import annotations
from typing import Optional, Any
import abc

from itertools import chain

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from socialnetwork.utils.user_control_decorator import user_controller

# A combined view for all calls to `://service/api/authors/{AUTHOR_SERIAL}/inbox`

_INBOX_HANDLERS: list[InboxHandler] = []


def register_inbox_handler(handler: InboxHandler) -> None:
    _INBOX_HANDLERS.append(handler)


class InboxHandler(abc.ABC):
    """InboxHandler class that handles a specific type of inbox item
    When calling __init__, pass in a list of types that this handler can handle
    Then, implement the post method to handle the POST request (it is already wrapped with user_controller, so feel free to call `user_control()` if needed)
    """

    def __init__(self, handlable_types: list[str]):
        self.handlable_types: list[str] = handlable_types

    def can_handle(self, type: str) -> bool:
        return type in self.handlable_types

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

    @method_decorator(user_controller())
    def post(self, request: Request, author_uuid: str) -> Response:
        """Send an inbox item to this author's inbox"""
        type = request.data.get("type")
        if type is None:
            return Response({"error": "missing 'type' field under inbox item"}, 400)
        handler = self._find_handler_for_type(type)
        if handler is not None:
            return handler.post(request)
        return Response({"error": "invalid 'type' field under inbox item",
                         "type": type}, 400)
