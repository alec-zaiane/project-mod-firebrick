
from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from comments.models import Comment
from likes.models import Like
from posts.models import Post, CONTENT_TYPE_WEB_MAP_REVERSE, CONTENT_TYPE_WEB_MAP
from likes.serializers import LikeSerializer
from user_management.models import Author, Node
from user_management.serializers import AuthorSerializer


class CommentSerializer(serializers.ModelSerializer[Comment]):
    """Comment serializer for node2node

    Example comment API object from the class docs:
    ```
    {
        "type":"comment",
        "author":{
            "type":"author",
            "id":"http://nodeaaaa/api/authors/111",
            "page":"http://nodeaaaa/authors/greg",
            "host":"http://nodeaaaa/api/",
            "displayName":"Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        "comment":"Sick Olde English",
        "contentType":"text/markdown",
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        // ID of the Comment
        "id": "http://nodeaaaa/api/authors/111/commented/130",
        "post": "http://nodebbbb/api/authors/222/posts/249",
        // likes on the comment
        "likes":{
            "type":"likes",
            // this may or may not be the same as page for the post
            // this may or may not be the same as page for the comment
            // depending if there's a seperate URL to just see the comments
            "page":"http://nodeaaaa/authors/222/posts/249"
            "id":"http://nodeaaaa/api/authors/111/commented/130/likes"
            // likes.page, likes.size, likes.count,
            // likes.src should be sent for comments on public and unlisted posts
            // in order to reduce API calls
            // You should return ~ 5 likes per post.
            // should be sorted newest(first) to oldest(last)
            // this is to reduce API call counts
            // number of the first page of likes
            "page_number":1,
            // size of a page of likes
            "size":50,
            // total number of likes
            "count": 9001,
            // the first page of likes
            "src":[
                {
                    "type":"like",
                    "author":{
                        "type":"author",
                        "id":"http://nodebbbb/api/authors/222",
                        "host":"http://nodebbbb/api/",
                        "displayName":"Lara Croft",
                        "page":"http://nodebbbb/authors/222",
                        "github": "http://github.com/laracroft",
                        "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
                    },
                    // ISO 8601 TIMESTAMP
                    "published":"2015-03-09T13:07:04+00:00",
                    // ID of the Comment (UUID)
                    "id": "http://nodeaaaa/api/authors/222/liked/255",
                    "object": "http://nodeaaaa/api/authors/111/commented/130"
                }
            ]
        },
    }
    ```
    """
    class Meta:
        model = Comment
        fields = ["author", "content", "content_type", "created_at", "post", "fqid", "likes"]

    def to_representation(self, instance: Comment) -> dict[str, Any]:
        if not isinstance(instance, Comment):
            raise ValueError(
                f"CommentSerializer can only serialize Comment objects, got {instance}")
        return {
            "type": "comment",
            "author": AuthorSerializer().to_representation(instance.author),
            "comment": instance.content,
            "contentType": CONTENT_TYPE_WEB_MAP.get(instance.content_type, None),
            "published": instance.created_at.isoformat(),
            "id": instance.fqid,
            "post": instance.post.fqid,
            "likes": LikeSerializer(instance.likes.all(), many=True).data
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("type") != "comment":
            raise ValidationError({"type": "Comment object must always have type comment"})
        if 'contentType' not in data:
            raise ValidationError({"contentType": "Missing contentType"})
        comment_type = CONTENT_TYPE_WEB_MAP_REVERSE.get(data["contentType"], None)
        if comment_type is None:
            raise ValidationError({
                "contentType": f"Unsupported content type {data['contentType']}, expected one of {list(CONTENT_TYPE_WEB_MAP_REVERSE.keys())}"
            })

        found_post = Post.visible_posts.find_by_fqid(data["post"])
        if found_post is None:
            raise ValidationError({
                "post": f"Could not find post with id {data['post']}"
            })

        # before returning, make sure all `likes` are accounted for in our database
        if data.get("likes"):
            for like in data["likes"]:
                like_dict = LikeSerializer().to_internal_value(like)
                Like.objects.get_or_create(**like_dict)

        found_author = AuthorSerializer().get_or_create(data["author"])
        if found_author is None:
            raise ValidationError(
                {"author": f"Could not find author with id {data['author']['id']}"})
        return {
            "author": found_author,
            "content": data["comment"],
            "content_type": comment_type,
            "created_at": data["published"],
            "post": found_post,
            "fqid": data["id"],
            "host_node": found_author.host_node,
        }

    def create(self, validated_data: dict[str, Any]) -> Comment:
        if "host_node" not in validated_data:
            # TODO this doesn't feel right, but maybe it works?
            validated_data["host_node"] = Node.objects.get_local_node()
        return Comment.objects.create(**validated_data)

    def get_or_create(self, data: dict[str, Any]) -> Comment:
        try:
            return Comment.objects.get_by_fqid(data["id"])
        except Comment.DoesNotExist:
            return self.create(self.to_internal_value(data))
