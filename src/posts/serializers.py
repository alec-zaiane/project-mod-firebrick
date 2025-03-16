from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from posts.models import Post, PostTypes
from user_management.models import Author
from user_management.serializers import AuthorSerializer
# from comments.serializers import CommentsSerializer
# from likes.serializers import LikesSerializer


class PostSerializer(serializers.ModelSerializer[Post]):
    """
    Post Serializer for node2node.

    Serializes Post objects into the expected API response format.

    Example:
    ```
    {
        "type":"post",
        "title":"DID YOU READ MY POST YET?",
        "id": "http://nodebbbb/api/authors/222/posts/293",
        // The frontend URL of this post
        "page": "http://nodebbbb/authors/222/posts/293",
        "description":"Whatever",
        "contentType":"text/plain",
        "content":"Are you even reading my posts Arjun?",
        "author":{
            "type":"author",
            "id":"http://nodebbbb/api/authors/222",
            "host":"http://nodebbbb/api/",
            "displayName":"Lara Croft",
            "page":"http://nodebbbb/authors/222",
            "github": "http://github.com/laracroft",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        "comments": {
            "type": "comments",
            "id": "http://nodebbbb/api/authors/222/posts/293/comments",
            // in this example nodebbbb has a html page just for the comments
            "page": "http://nodebbbb/authors/222/posts/293/comments",
            "page_number": 1,
            "size": 5,
            "count": 0,
            "src": [],
        },
        "likes": {
            "type": "likes",
            "id": "http://127.0.0.1:5454/api/authors/222/posts/293/likes",
            // in this example nodebbbb has a html page just for the likes
            "page": "http://nodebbbb/authors/222/posts/293/likes"
            "page_number": 1,
            "size": 50,
            "count": 0,
            "src": [],
        },
        "published":"2015-03-09T13:07:04+00:00",
        "visibility":"FRIENDS"
    }
    ```
    """

    class Meta:
        model = Post
        fields = ["uuid", "title", "description", "content",
                  "post_type", "visibility_type", "author", "published"]

    def to_representation(self, instance: Post) -> dict[str, Any]:
        """Convert a Post instance into a dictionary following the expected schema."""
        if not isinstance(instance, Post):
            raise ValueError(
                f"PostSerializer can only serialize Post objects, got {type(instance)}")

        # Determine the content type
        content_type_map: dict[str, str] = {
            PostTypes.PLAINTEXT: "text/plain",
            PostTypes.MARKDOWN: "text/markdown",
            # check back on this
            PostTypes.IMAGE: "image/png;base64",
            # this isn't implemented yet
            PostTypes.VIDEO: "application/base64"
        }
        content_type = content_type_map.get(instance.post_type)

        return {
            "type": "post",
            "title": instance.title,
            "id": instance.fqid,
            "description": instance.description,
            "contentType": content_type,
            "content": instance.content,
            "author": AuthorSerializer(instance.author).data,
            # "comments": CommentsSerializer(instance.comments.all(), many=True).data,
            # "likes": LikesSerializer(instance.likes.all(), many=True).data,
            "published": instance.created_at.isoformat(),
            "visibility": instance.visibility_type,
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON data into a dictionary compatible with Post model."""
        if data.get("type") != "post":
            raise ValidationError("Post object must always have type 'post'")

        content_type_map = {
            "text/plain": PostTypes.PLAINTEXT,
            "text/markdown": PostTypes.MARKDOWN,
            "image/png;base64": PostTypes.IMAGE,
            "image/jpeg;base64": PostTypes.IMAGE,
            "application/base64": PostTypes.VIDEO,
        }

        post_type = content_type_map.get(data["contentType"], None)
        if post_type is None:
            raise ValidationError(f"Invalid contentType: {data['contentType']}")

        return {
            "title": data["title"],
            "fqid": data["id"],
            "description": data["description"],
            "post_type": post_type,  # contentType
            "content": data["content"],
            "author": Author.objects.get_by_fqid(data["author"]["id"]),
            "visibility_type": data["visibility"],
        }
