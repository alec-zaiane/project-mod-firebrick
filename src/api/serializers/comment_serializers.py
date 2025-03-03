from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer
from api.serializers.like_serializers import LikesSerializer


class CommentSerializer(serializers.Serializer[Any]):
    """Comment Serializer for node2node
    Example Comment API object from the class docs:
    ```
    {
        "type":"comment",
        "author": {
            /* author object */
        }
        "comment":"Sick Olde English",
        "contentType":"text/markdown",
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        // ID of the Comment
        "id": "http://nodeaaaa/api/authors/111/commented/130",
        "post": "http://nodebbbb/api/authors/222/posts/249",
        // likes on the comment
        "likes": {
            /* likes object */
        }
    }
    ```
    """
    type = serializers.CharField(
        default="comment",
        validators=[custom_validators.ExactlyEqualTo("comment")])
    author = AuthorSerializer()
    comment = serializers.CharField()
    contentType = serializers.CharField(validators=[custom_validators.IsInSet({
        "text/markdown", "text/plain"
    })])
    published = serializers.DateTimeField(format='iso-8601')
    id = serializers.URLField()
    post = serializers.URLField()
    likes = LikesSerializer()


class CommentsSerializer(serializers.Serializer[Any]):
    """Comment list serializer for node2node
    Example comments api object from the class docs:
    ```
    {
        "type":"comments",
        // this may or may not be the same as page for the post,
        // depending if there's a seperate URL to just see the comments
        "page":"http://nodebbbb/authors/222/posts/249",
        "id":"http://nodebbbb/api/authors/222/posts/249/comments"
        // comments.page, comments.size, comments.count,
        // comments.src are only sent if:
        // * public
        // * unlisted
        // * friends-only and sending it to a friend
        // You should return ~ 5 comments per post.
        // should be sorted newest(first) to oldest(last)
        // this is to reduce API call counts
        // number of the first page of comments
        "page_number":1,
        // size of comment pages
        "size":5,
        // total number of comments for this post
        "count": 1023,
        // the first page of comments
        "src": [
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ }
        ]
    }
    ```
    """
    type = serializers.CharField(
        default="comments",
        validators=[custom_validators.ExactlyEqualTo("comments")])
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField(min_value=1)
    size = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    src = serializers.ListField(child=CommentSerializer())
