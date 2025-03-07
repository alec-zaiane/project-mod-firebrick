from typing import Any

from django.urls import reverse

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer
from api.serializers.like_serializers import LikesSerializer

from socialnetwork.models import Comment, PostDifferentiator, Post
from socialnetwork.utils.get_object_by_fqid import get_object_by_fqid

from project_firebrick.settings import THIS_NODE_URL


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
    published = serializers.DateTimeField(format='iso-8601', required=False)
    id = serializers.URLField(required=False)
    post = serializers.URLField()
    likes = LikesSerializer(required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a CommentSerializer
        Either initialize normally, or pass in a Comment object as arg 0 to make it from a Comment"""
        found_comment: Comment | None = None
        if args and isinstance(args[0], Comment):
            found_comment = args[0]

        if found_comment is None:  # we're not making this from a Comment, let the superclass handle it
            super().__init__(*args, **kwargs)

        else:  # we're making this from a Comment
            assert found_comment.post.author is not None, "This post was deleted, edge case"  # TODO
            type = "comment"
            author_serializer = AuthorSerializer(found_comment.author)
            if not author_serializer.is_valid():
                raise serializers.ValidationError(author_serializer.errors)
            author = author_serializer.data
            comment = found_comment.comment
            contentType = found_comment.comment_type
            published = found_comment.date_created
            id = f"{THIS_NODE_URL}{reverse("api:commented_serial", args=[found_comment.author.uuid, found_comment.uuid])}"
            post = f"{THIS_NODE_URL}{reverse('api:post_author_specific', args=[found_comment.post.author.uuid, found_comment.post.uuid])}"
            likes = LikesSerializer(found_comment.get_likes()).data
            super().__init__(data={
                "type": type,
                "author": author,
                "comment": comment,
                "contentType": contentType,
                "published": published,
                "id": id,
                "post": post,
                "likes": likes
            })
            self.is_valid()

    def create(self, validated_data: dict[str, Any]) -> Comment:
        """Create a Comment from the validated data"""
        post = get_object_by_fqid(validated_data["post"])
        if not isinstance(post, Post):
            raise serializers.ValidationError
        post_diff = PostDifferentiator.create_differentiator_for_post(
            post)
        author_serializer = AuthorSerializer(data=validated_data["author"])
        if not author_serializer.is_valid():
            raise serializers.ValidationError(author_serializer.errors)
        return Comment.objects.create(
            author=author_serializer.get_mentioned_author(),
            comment=validated_data["comment"],
            comment_type=validated_data["contentType"],
            _post_differentiator=post_diff
        )


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
