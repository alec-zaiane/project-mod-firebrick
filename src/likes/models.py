from __future__ import annotations

from typing import Any, cast, Optional

from django.db import models
from django.core.exceptions import ValidationError

from user_management.models import Author
from posts.models import Post
from comments.models import Comment

from core.utils.api_object import ApiObject, ApiObjectManager


class LikeManager(ApiObjectManager["Like"]):
    def create(self, *args: Any, **kwargs: Any) -> Like:
        author = kwargs.get("author")
        assert isinstance(author, Author)
        host_node = author.host_node
        return super().create(host_node=host_node, *args, **kwargs)

    def create_like(self, author: Author, target: Post | Comment) -> Like:
        """Create a new like for a post or commment.

        Raises a ValidationError if the target has already been liked by the author.
        """
        if isinstance(target, Post):
            if author.likes.filter(_target_post=target).exists():
                raise ValidationError("Post has already been liked")
            return self.create(author=author, _target_post=target)
        elif isinstance(target, Comment):
            if author.likes.filter(_target_comment=target).exists():
                raise ValidationError("Comment has already been liked")
            return self.create(author=author, _target_comment=target)
        else:
            raise ValueError("Target must be a post or comment")


class PostLikeManager(LikeManager):
    def get_queryset(self) -> models.QuerySet[PostLike]:
        return cast(models.QuerySet[PostLike], super().get_queryset().filter(_target_post__isnull=False))


class CommentLikeManager(LikeManager):
    def get_queryset(self) -> models.QuerySet[CommentLike]:
        return cast(models.QuerySet[CommentLike], super().get_queryset().filter(_target_comment__isnull=False))


class Like(ApiObject):
    author: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="likes")

    _target_post: models.ForeignKey[Post, Optional[Post]] = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    _target_comment: models.ForeignKey[Comment, Optional[Comment]] = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)

    @property
    def target(self) -> Post | Comment:
        raise NotImplementedError("Like must be a PostLike or CommentLike")

    objects: LikeManager = LikeManager()
    post_likes = PostLikeManager()
    comment_likes = CommentLikeManager()

    def clean(self) -> None:
        if not self._target_post and not self._target_comment:
            raise ValidationError("Like must have a target post or comment")
        if self._target_post and self._target_comment:
            raise ValidationError("Like cannot have both a target post and comment")
        super().clean()

    def generate_fqid(self) -> str:
        return f"{self.host_node.host_url}/likes/{self.uuid}"  # TODO replace with reverse() call :)


class PostLike(Like):
    class Meta:
        proxy = True

    @property
    def target(self) -> Post:
        if not self._target_post:
            raise ValidationError("PostLike must have a target post, this should never happen")
        return self._target_post


class CommentLike(Like):
    class Meta:
        proxy = True

    @property
    def target(self) -> Comment:
        if not self._target_comment:
            raise ValidationError(
                "CommentLike must have a target comment, this should never happen")
        return self._target_comment
