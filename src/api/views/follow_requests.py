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
from api.views.inbox import InboxHandler, register_inbox_handler

"""Follow request API view

Details from class page:
- URL: `://service/api/authors/{AUTHOR_SERIAL}/inbox`
    - POST [remote]: send a follow request to AUTHOR_SERIAL
- When author 1 tries to follow author 2, author 1's node send the follow request to author 2's node.
- If the author 2 accepts the Follow Request then author 1 is following author 2.
- If author 2 is also already following author 1, then they are now friends.
- Sent to inbox of "object"
"""


# This is done with the InboxHandler class because the /inbox endpoint must handle multiple types of requests
class FollowRequestInboxHandler(InboxHandler):
    def __init__(self) -> None:
        super().__init__("follow_request")

    @property
    def serializer(self) -> type[serializers.FollowRequestSerializer]:
        return serializers.FollowRequestSerializer

    def post(self, request: Request) -> Response:
        raise NotImplementedError("TODO")


register_inbox_handler(FollowRequestInboxHandler())
