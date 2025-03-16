from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from posts.models import Post, PostTypes
from user_management.models import Author
from user_management.serializers import AuthorSerializer
from api.serializers.comment_serializers import CommentsSerializer
from api.serializers.like_serializers import LikesSerializer


class PostSerializer(serializers.ModelSerializer[Post]):
    """
    Post Serializer for node2node.
    Serializes Post objects into the expected API response format.
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
            "id": instance.fqid,
            "title": instance.title,
            "description": instance.description,
            "contentType": content_type,
            "content": instance.content,
            "author": AuthorSerializer(instance.author).data,
            "comments": CommentsSerializer(instance.comments.all(), many=True).data,
            "likes": LikesSerializer(instance.likes.all(), many=True).data,
            "published": instance.published.isoformat(),
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

        post_type = content_type_map.get(data["contentType"])
        if post_type is None:
            raise ValidationError(f"Invalid contentType: {data['contentType']}")

        return {
            "fqid": data["id"],
            "title": data["title"],
            "description": data["description"],
            "content": data["content"],
            "post_type": post_type,
            "visibility_type": data["visibility"],
            "author": Author.objects.get_by_fqid(data["author"]["id"]),
        }

    def create(self, validated_data: dict[str, Any]) -> Post:
        """Create a new Post object from validated data."""
        fqid = validated_data.pop("fqid")
        return Post.objects.create(fqid=fqid, **validated_data)
