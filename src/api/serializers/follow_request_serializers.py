from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer


class FollowRequestSerializer(serializers.Serializer[Any]):
    """Follow request serializer for node2node
    Example Follow Request API object from the class docs:
    ```
    {
        "type": "follow",
        "summary":"Greg wants to follow Lara",
        "actor":{
            /* Author object who is sending the request */
        },
        "object":{
            /* Author object who is receiving the request */
        }
    }
    ```
    """
    type = serializers.CharField(default="follow", validators=[
                                 custom_validators.ExactlyEqualTo("follow")])
    summary = serializers.CharField()
    actor = AuthorSerializer()
    object = AuthorSerializer()
