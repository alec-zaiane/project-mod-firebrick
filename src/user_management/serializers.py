
from typing import Any
from collections.abc import Iterable


from django.urls import reverse
from rest_framework import serializers

from core.utils import custom_validators

from user_management.models import Author, Node, FollowRequest


class AuthorSerializer(serializers.Serializer[Author]):
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
    type = serializers.CharField(default="author", validators=[
                                 custom_validators.ExactlyEqualTo("author")])
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField(required=False)
    profileImage = serializers.URLField()
    page = serializers.URLField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an authorSerializer
        Either initialize normally, or pass in an Author object as arg 0 to make it from an Author"""
        author: Author | None = None
        if args and isinstance(args[0], Author):
            author = args[0]

        if author is None:
            super().__init__(*args, **kwargs)
        else:
            THIS_NODE_URL = Node.objects.get_local_node().host_url
            type = "author"
            id = f"{THIS_NODE_URL}{reverse("api:author", args=[author.uuid])}"
            host = f"{THIS_NODE_URL}{reverse("api:root")}"
            displayName = author.display_name
            profileImage = author.profile_image
            page = f"{THIS_NODE_URL}{reverse("socialnetwork:author_profile", args=[author.uuid])}"
            super().__init__(data={
                "type": type,
                "id": id,
                "host": host,
                "displayName": displayName,
                "profileImage": profileImage,
                "page": page
            })
            self.is_valid()

    def save(self, **kwargs: Any) -> Any:
        pass  # TODO

    def get_mentioned_author(self) -> Author:
        """Get the Author object mentioned by this serializer
        **Must be called after is_valid()**
        raises Author.DoesNotExist if the author does not exist
        """
        full_url = self.validated_data["id"]
        assert isinstance(full_url, str)  # for type checking
        return Author.objects.get_by_fqid(full_url)

    def check_author_exists(self) -> bool:
        try:
            self.get_mentioned_author()
            return True
        except Author.DoesNotExist:
            return False


class AuthorsSerializer(serializers.Serializer[Any]):
    """Author list serializer for node2node
    Example Authors API object from the class docs:
    ```
    {
        "type": "authors",
        "authors":[
            {
                "type":"author",
                "id":"http://nodeaaaa/api/authors/111",
                "host":"http://nodeaaaa/api/",
                "displayName":"Greg Johnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "page": "http://nodeaaaa/authors/greg"
            },
            {
                // A second author object...
            },
            {
                // A third author object...
            }
        ]
    }
    ```
    """
    type = serializers.CharField(default="authors", validators=[
                                 custom_validators.ExactlyEqualTo("authors")])

    authors = serializers.ListField(child=AuthorSerializer())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an AuthorsSerializer from an iterable of Authors"""
        authors = []
        authors_found = False
        if args and isinstance(args[0], Iterable):
            authors_found = True
            for author in args[0]:
                print("author:", author)
                authors.append(AuthorSerializer(author).data)

        if not authors_found:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(data={
                "type": "authors",
                "authors": authors
            })
            self.is_valid()


class FollowRequestSerializer(serializers.Serializer[FollowRequest]):
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

    def create(self, validated_data: dict[str, Any]) -> FollowRequest:
        assert isinstance(self.validated_data["actor"], Author)
        assert isinstance(self.validated_data["object"], Author)
        return FollowRequest.objects.create_follow_request(
            follower=self.validated_data["actor"],
            followee=self.validated_data["object"]
        )
