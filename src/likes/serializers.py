from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from likes.models import Like
from user_management.models import Author
from user_management.serializers import AuthorSerializer
from posts.models import Post
from comments.models import Comment


class LikeSerializer(serializers.ModelSerializer[Like]):
    """Like serializer for node2node

    Example like API object from the class docs:
    ```
    {
        "type":"like",
        "author":{
            "type":"author",
            "id":"http://nodeaaaa/api/authors/111",
            "page":"http://nodeaaaa/authors/greg",
            "host":"http://nodeaaaa/api/",
            "displayName":"Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        "id":"http://nodeaaaa/api/authors/111/liked/166",
        // ID of the Comment (UUID)
        "object": "http://nodebbbb/api/authors/222/posts/249"
    }
    ```
    """

    class Meta:
        model = Like
        fields = ["author", "created_at", "fqid", "_target_post", "_target_comment"]

    def to_representation(self, instance: Like) -> dict[str, Any]:
        if not isinstance(instance, Like):
            raise ValueError(f"LikeSerializer can only serialize Like objects, got {instance}")
        return {
            "type": "like",
            "author": AuthorSerializer().to_representation(instance.author),
            "published": instance.created_at.isoformat(),
            "id": instance.fqid,
            "object": instance.target.fqid,
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("type") != "like":
            raise ValidationError({"type": "Like object must always have type like"})
        if 'object' not in data:
            raise ValidationError({"object": "Like object must have an object field"})
        maybe_post = Post.visible_posts.find_by_fqid(data["object"])
        maybe_comment = Comment.objects.find_by_fqid(data["object"])
        if maybe_post is None and maybe_comment is None:
            raise ValidationError({
                "object": f"Could not find post or comment with id {data['object']}"
            })
        return {
            "author": data["author"],
            "fqid": data["id"],
            "created_at": data["published"],
            "_target_post": maybe_post,
            "_target_comment": maybe_comment,
        }

    def create(self, validated_data: dict[str, Any]) -> Like:
        author = validated_data.get("author")
        if isinstance(author, dict):
            author = Author.objects.find_by_fqid(author["id"])
        if not isinstance(author, Author):
            raise ValueError(f"author must be an Author object, got {author}")
        target = self.get_target()
        return Like.objects.create_like(author, target)

    def get_target(self) -> Post | Comment:
        if self.validated_data.get("_target_post") is not None:
            return self.validated_data["_target_post"]
        return self.validated_data["_target_comment"]
