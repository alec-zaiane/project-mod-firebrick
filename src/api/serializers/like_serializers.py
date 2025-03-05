from typing import Any

from django.urls import reverse
from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer

from socialnetwork.models import Like, Author, Post, Comment, PostDifferentiator, PostTextBased, PostMediaBased
from socialnetwork.utils.get_object_by_fqid import get_object_by_fqid


class LikeSerializer(serializers.Serializer[Any]):
    """Like Serializer for node2node
    Example Like API object from the class docs:
    ```
    {
        "type":"like",
        "author":{
            /* author object */
        },
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        "id":"http://nodeaaaa/api/authors/111/liked/166",
        // ID of either the post or the comment that this like is for
        "object": "http://nodebbbb/api/authors/222/posts/249"
    }
    ```
    """
    type = serializers.CharField(
        default="like",
        validators=[custom_validators.ExactlyEqualTo("like")])
    author = AuthorSerializer()
    published = serializers.DateTimeField(format='iso-8601')
    id = serializers.URLField(required=False)
    object = serializers.URLField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a LikeSerializer
        Either pass in a socialnetwork.models.Like object as the first argument
        to make a serializer from a Like object, or initialize normally"""

        if args and isinstance(args[0], Like):
            like = args[0]
            author = AuthorSerializer(like.author)
            data = {
                "type": "like",
                "author": author.data,
                "published": like.date_created,
                "id": like.get_id_url(),
                "object": like.get_target_url()
            }
            super().__init__(data, **kwargs)
        else:
            super().__init__(*args, **kwargs)

    def create(self, validated_data: dict[str, Any]) -> Like:
        """Create a Like object from the validated data
        If the author or target object does not exist, raise a ValidationError"""
        author_data = validated_data.pop("author")
        author_serializer = AuthorSerializer(data=author_data)
        if not author_serializer.is_valid():
            raise serializers.ValidationError(author_serializer.errors)
        if not author_serializer.check_author_exists():
            raise serializers.ValidationError("Author does not exist")
        author = author_serializer.get_mentioned_author()
        try:
            target = self.get_target()
        except SyntaxError:
            raise serializers.ValidationError("Invalid object FQID")
        except NotImplementedError:
            raise serializers.ValidationError("Unsupported object type")
        except ValueError:
            raise serializers.ValidationError("Object does not exist")
        if isinstance(target, Post):
            if isinstance(target, PostTextBased):
                post_diff = PostDifferentiator.objects.create(
                    _post_text=target)
            elif isinstance(target, PostMediaBased):
                post_diff = PostDifferentiator.objects.create(
                    _post_media=target)
            else:
                raise ValueError("Unsupported post type")
            return Like.objects.create(author=author, target_post_differentiator=post_diff)
        elif isinstance(target, Comment):
            return Like.objects.create(author=author, target_comment=target)
        else:
            raise serializers.ValidationError("Unsupported object type")

    def get_target(self) -> Post | Comment:
        """Get the target object of the like

        **must be called after is_valid()**
        """
        target = get_object_by_fqid(self.validated_data["object"])
        assert isinstance(target, Post) or isinstance(
            target, Comment), f"This should never happen, target is {target}, not Post or Comment"
        return target


class LikesSerializer(serializers.Serializer[Any]):
    """Like list serializer for node2node
    Example likes API object from the class docs:
    '''
    {
        "type":"likes",
        // this may or may not be the same as page for the post,
        // depending if there's a seperate URL to just see the comments
        "page":"http://nodeaaaa/authors/222/posts/249"
        "id":"http://nodeaaaa/api/authors/222/posts/249/likes"
        // likes.page, likes.size, likes.count,
        // likes.src should be sent for public and unlisted posts
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
        "src" [
            { /* like object */ }
            { /* like object */ }
        ]
    }
    '''
    """
    type = serializers.CharField(
        default="likes",
        validators=[custom_validators.ExactlyEqualTo("likes")]
    )
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField(min_value=1)
    size = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    src = serializers.ListField(child=LikeSerializer())
