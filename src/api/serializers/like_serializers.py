from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer


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
        // ID of the Comment (UUID)
        "object": "http://nodebbbb/api/authors/222/posts/249"
    }
    ```
    ? how does the like for posts look?
    """
    type = serializers.CharField(
        default="like",
        validators=[custom_validators.ExactlyEqualTo("like")])
    author = AuthorSerializer()
    published = serializers.DateTimeField(format='iso-8601')
    id = serializers.URLField()
    object = serializers.URLField()


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
