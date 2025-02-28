from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators


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
