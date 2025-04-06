from typing import TYPE_CHECKING, Any, Optional

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
        return self.create(host_node=post.host_node, author=author, post=post, content=content, content_type=content_type)


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
        return f"{self.host_node.host_url}/comments/{self.uuid}".replace("/api/api", "/api")

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

    def _propagate_post_save_to_other_nodes(self, created: bool) -> None:
        if not created:
            return super()._propagate_post_save_to_other_nodes(created)
        # if this is new, we need to send it to the inbox of the author of the post, as well as all of their followers
        recipients = [self.post.author] + list(self.post.author.followers.all())
        for recipient in recipients:
            if recipient.host_node.is_local_node:
                # don't send to self
                return
            # send to the inbox of the author of the post
            recipient.host_node.send_create(
                self.node2node_encode_as_class_json_dict(),
                to=self.node2node_get_creation_url(recipient)
            )

    def node2node_get_creation_url(self, author_for_inbox: Optional[Author] = None) -> str:
        if not author_for_inbox:
            return reverse("comments:node2node_comments-list")
        return author_for_inbox.node2node_get_inbox_url()

    def node2node_get_update_url(self, author_for_inbox: Optional[Author] = None) -> str:
        return self.fqid
        # return reverse("comments:node2node_comments-detail", kwargs={"uuid": self.uuid})

    def node2node_get_deletion_url(self, author_for_inbox: Optional[Author] = None) -> str:
        return self.node2node_get_update_url()
