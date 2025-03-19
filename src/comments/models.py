from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from likes.models import Like

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.utils.api_object import AuthoredApiObject, ApiObjectManager
from user_management.models import Author
from posts.models import Post, PostTypes

SUPPORTED_COMMENT_TYPES = [PostTypes.PLAINTEXT, PostTypes.MARKDOWN]

# Create your models here.


class CommentManager(ApiObjectManager["Comment"]):
    def create_comment(self, author: Author, post: Post, content: str) -> "Comment":
        return self.create(host_node=author.host_node, author=author, post=post, content=content)


class Comment(AuthoredApiObject):
    author: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="comments")
    post: models.ForeignKey[Post, Post] = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content: models.TextField[str, str] = models.TextField(_("Content"))
    content_type: models.CharField[str, str] = models.CharField(
        _("Content type"), max_length=3, choices=PostTypes.choices, default=PostTypes.PLAINTEXT)

    if TYPE_CHECKING:
        likes: models.QuerySet[Like]

    objects: CommentManager = CommentManager()

    def generate_fqid(self) -> str:
        # TODO replace with reverse() call :)
        return f"{self.host_node.host_url}/comments/{self.uuid}"

    def clean(self) -> None:
        super().clean()
        if self.content_type not in SUPPORTED_COMMENT_TYPES:
            raise ValidationError(f"Unsupported content type {self.content_type}")
