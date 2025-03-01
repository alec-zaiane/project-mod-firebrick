from typing import Any

from django.urls import reverse

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators

from socialnetwork.models import Author

from project_firebrick.settings import THIS_NODE_URL


class AuthorSerializer(serializers.Serializer[Any]):
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
        // URL of the user's github
        "github": "http://github.com/gjohnson",
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
    displayName = serializers.CharField()
    github = serializers.URLField(
        validators=[custom_validators.ContainsValidator("github.com")])
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
            type = "author"
            # TODO make this a reverse() call
            id = f"{THIS_NODE_URL}/api/authors/{author.uuid}"
            host = f"{THIS_NODE_URL}{reverse("api:root")}"
            # TODO make a display name model field for all authors
            displayName = f"Author's Display Name"
            github = f"https://github.com/uofa-cmput404"
            profileImage = f"https://fastly.picsum.photos/id/391/200/200.jpg"
            page = f"{THIS_NODE_URL}{reverse("socialnetwork:author_profile", args=[author.uuid])}"
            super().__init__(data={
                "type": type,
                "id": id,
                "host": host,
                "displayName": displayName,
                "github": github,
                "profileImage": profileImage,
                "page": page
            })
            self.is_valid()
