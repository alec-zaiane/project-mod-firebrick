from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from likes.models import Like

from django.db import models

from django.utils.translation import gettext_lazy as _

from core.utils.api_object import ApiObject, ApiObjectManager
from user_management.models import Author
from posts.models import Post

# Create your models here.


class CommentManager(ApiObjectManager["Comment"]):
    def create_comment(self, author: Author, post: Post, content: str) -> "Comment":
        return self.create(host_node=author.host_node, author=author, post=post, content=content)


class Comment(ApiObject):
    author: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="comments")
    post: models.ForeignKey[Post, Post] = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content: models.TextField[str, str] = models.TextField(_("Content"))

    if TYPE_CHECKING:
        likes: models.QuerySet[Like]

    objects: CommentManager = CommentManager()

    def generate_fqid(self) -> str:
        # TODO replace with reverse() call :)
        return f"{self.host_node.host_url}/comments/{self.uuid}"
