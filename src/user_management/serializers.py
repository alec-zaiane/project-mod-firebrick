
from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from user_management.models import Author, FollowRequest, Node


class AuthorSerializer(serializers.ModelSerializer[Author]):
    """Author Serializer for node2node

    Example Author API object from the class docs:
    ```
    {
        // Author object must always have type author
        "type":"author",
        // The full API URL for the author
        "id":"http://nodeaaaa/api/authors/111",
        // The full API URL for the author's node
        "host":"http://nodeaaaa/api/",
        // How the user would like the name to be displayed
        "displayName":"Greg Johnson",
        // URL of the user's profile image (external image in this example)
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        // URL of the user's HTML profile page
        // It could include an id number/uuid or not
        "page": "http://nodeaaaa/authors/greg"
    }
    ```
    """
    class Meta:
        model = Author
        fields = ["uuid", "display_name", "profile_image"]

    def to_representation(self, instance: Author) -> dict[str, Any]:
        if not isinstance(instance, Author):
            raise ValueError(f"AuthorSerializer can only serialize Author objects, got {instance}")
        author_node_url = instance.host_node.host_url
        return {
            "type": "author",
            "id": instance.fqid,
            "host": author_node_url,
            "displayName": instance.display_name,
            "profileImage": instance.profile_image,
            "page": instance.page_url,
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("type") != "author":
            raise ValidationError("Author object must always have type author")
        return {
            "fqid": data["id"],
            "host__host_url": data["host"],
            "display_name": data["displayName"],
            "profile_image": data["profileImage"],
            "page_url": data["page"],
        }

    def create(self, validated_data: dict[str, Any]) -> Author:
        fqid = validated_data.pop("fqid")
        return Author.objects.create(fqid=fqid, **validated_data)


class FollowRequestSerializer(serializers.ModelSerializer[FollowRequest]):
    class Meta:
        model = FollowRequest
        fields = ["follower", "followee"]

    def to_representation(self, instance: FollowRequest) -> dict[str, Any]:
        return {
            "type": "follow",
            "summary": f"{instance.follower.display_name} wants to follow {instance.followee.display_name}",
            "actor": AuthorSerializer(instance.follower).data,
            "object": AuthorSerializer(instance.followee).data,
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("type") != "follow":
            raise ValidationError("Follow request object must always have type follow")
        return {
            "follower": Author.objects.get_by_fqid(data["actor"]["id"]),
            "followee": Author.objects.get_by_fqid(data["object"]["id"]),
        }
