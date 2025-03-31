from typing import Any
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from posts.models import Post, CONTENT_TYPE_WEB_MAP, CONTENT_TYPE_WEB_MAP_REVERSE, VISIBILITY_TYPE_WEB_MAP, VISIBILITY_TYPE_WEB_MAP_REVERSE
from comments.models import Comment
from user_management.models import Author
from user_management.serializers import AuthorSerializer
from comments.serializers import CommentSerializer
from likes.models import Like
from likes.serializers import LikeSerializer


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
                  "post_type", "visibility_type", "author", "created_at"]

    def to_representation(self, instance: Post) -> dict[str, Any]:
        """Convert a Post instance into a dictionary following the expected schema."""
        if not isinstance(instance, Post):
            raise ValueError(
                f"PostSerializer can only serialize Post objects, got {type(instance)}")

        # Determine the content type
        content_type = CONTENT_TYPE_WEB_MAP.get(instance.post_type)

        return {
            "type": "post",
            "title": instance.title,
            "id": instance.fqid,
            "description": instance.description,
            "contentType": content_type,
            "content": instance.content,
            "author": AuthorSerializer(instance.author).data,
            "comments": {"type": "comments",
                         "src": CommentSerializer(instance.comments.all(), many=True).data
                         },
            "likes": {"type": "likes",
                      "src": LikeSerializer(instance.likes.all(), many=True).data,
                      },
            "published": instance.created_at.isoformat(),
            "visibility": VISIBILITY_TYPE_WEB_MAP.get(instance.visibility_type),
        }

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON data into a dictionary compatible with Post model."""
        if data.get("type") != "post":
            raise ValidationError({
                "type": "Post object must always have type 'post'"
            })
        if "contentType" not in data:
            raise ValidationError({
                "contentType": "Post object must always have contentType"
            })

        post_type = CONTENT_TYPE_WEB_MAP_REVERSE.get(data["contentType"], None)
        if post_type is None:
            raise ValidationError(f"Invalid contentType: {data['contentType']}")

        author = AuthorSerializer().get_or_create(data["author"])

        return {
            "title": data["title"],
            "fqid": data["id"],
            "description": data["description"],
            "post_type": post_type,  # contentType
            "content": data["content"],
            "author": author,
            "visibility_type": VISIBILITY_TYPE_WEB_MAP_REVERSE.get(data["visibility"]),
        }

    def create(self, validated_data: dict[str, Any]) -> Post:
        """Create a new Post object from validated data."""
        fqid = validated_data.pop("fqid")
        if not fqid:
            raise ValidationError("Post must have a valid FQID.")
        author: Author = validated_data["author"]
        host_node = author.host_node
        return Post.objects.create(fqid=fqid, **validated_data, host_node=host_node)

    def get_or_create(self, data: dict[str, Any]) -> Post:
        # if a post doesn't exist, create it, otherwise update and return it
        post_dict = self.to_internal_value(data)
        post = Post.objects.find_by_fqid(post_dict["fqid"])
        if post is None:
            post = self.create(post_dict)
        else:
            for key, value in post_dict.items():
                setattr(post, key, value)
            post.save()
        return post
