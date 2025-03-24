from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from likes.models import Like

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from core.utils.api_object import AuthoredApiObject, ApiObjectManager
from user_management.models import Author
from posts.models import Post, PostTypes

SUPPORTED_COMMENT_TYPES = [PostTypes.PLAINTEXT, PostTypes.MARKDOWN]

# Create your models here.


class CommentManager(ApiObjectManager["Comment"]):
    def create_comment(self, author: Author, post: Post, content: str, content_type: PostTypes) -> "Comment":
        return self.create(host_node=author.host_node, author=author, post=post, content=content, content_type=content_type)


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
        return f"{self.host_node.host_url}comments/{self.uuid}".replace("/api/api", "/api")

    def clean(self) -> None:
        super().clean()
        if self.content_type not in SUPPORTED_COMMENT_TYPES:
            raise ValidationError(f"Unsupported content type {self.content_type}")

    def check_can_be_seen_by(self, viewer: Author) -> bool:
        # TODO align with "As an author, comments on my friends-only posts are visible only to my friends and the comment's author."
        return self.post.check_can_be_seen_by(viewer)

    # node2node stuff
    def node2node_encode_as_class_json_dict(self) -> dict[str, Any]:
        from comments.serializers import CommentSerializer
        return CommentSerializer().to_representation(self)

    def node2node_get_creation_url(self) -> str:
        return reverse("comments:node2node_comments-list")

    def node2node_get_update_url(self) -> str:
        return reverse("comments:node2node_comments-detail", kwargs={"fqid": self.get_encoded_fqid()})

    def node2node_get_deletion_url(self) -> str:
        return self.node2node_get_update_url()
