from __future__ import annotations
import uuid
from typing import Any, Collection

from datetime import datetime

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import QuerySet

from typing import Optional
from django.contrib.auth.models import User

from django.db.models import Q
from itertools import chain
from project_firebrick.settings import THIS_NODE_URL


class RemoteNode(models.Model):
    # TODO will contain fields for the remote nodes that this instance knows about
    pass


class Author(models.Model):
    """
    This is an abstract class that must not be instantiated, use one of the subclasses below
    Makes posts
        Following other authors
        Can have followers
        Makes friends
        Likes posts
        Comments on posts
        A generally nice person
        Can register with the admins approval
        Can find other authors by using the public timeline
    """

    # Fields
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers', blank=True)
    bio = models.TextField(blank=True)
    display_name = models.CharField(max_length=128)
    # 2048 is the character limit for URLs
    profile_image = models.URLField(blank=True)

    # Computed Properties
    @property
    def followers(self) -> models.QuerySet[Author]:
        return Author.objects.filter(following=self)

    @property
    def friends(self) -> list[Author]:
        following_set = set(self.following.all())
        followers_set = set(self.followers.all())
        return list(following_set.intersection(followers_set))

    @property
    def username(self) -> str:
        if isinstance(self, LocalAuthor):
            return self.user.username
        elif isinstance(self, RemoteAuthor):
            return self.username
        raise SyntaxError(
            "Author objects should never be instantiated directly")

    @property
    def posts(self) -> list[Post]:
        # get all posts by this author
        text_posts = PostTextBased.objects.filter(base_author=self)
        media_posts = PostMediaBased.objects.filter(base_author=self)
        return sorted(
            chain(text_posts, media_posts),
            key=lambda post: post.date_created,
            reverse=True
        )
    # Methods

    def get_is_friends_with(self, other: Author) -> bool:
        """Returns true if this author is friends with the other author"""
        self_is_following_other = other.following.filter(pk=self.pk).exists()
        other_is_following_self = self.following.filter(pk=other.pk).exists()
        return self_is_following_other and other_is_following_self

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Delete this author"""
        # keep all posts from this author until an admin deletes them
        self.following.clear()
        for post in self.posts:
            post.base_author = None
            post.delete()
            post.save()

        if isinstance(self, LocalAuthor):
            self.user.delete()
        return super().delete(*args, **kwargs)

    @classmethod
    def get_author_by_FQID(cls, fqid: str) -> Author:
        # not sure if this is the best place to put this, but we need a centralized place for it to go
        raise NotImplementedError("TODO")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Author):
            return False
        return self.uuid == other.uuid

        # TODO when adding remote nodes, we'll need something like this:
        # # if we're both LocalAuthors, compare the uuid
        # if isinstance(self, LocalAuthor) and isinstance(other, LocalAuthor):
        #     return self.uuid == other.uuid
        # # if we're both RemoteAuthors, do something else
        # if isinstance(self, RemoteAuthor) and isinstance(other, RemoteAuthor):
        #     raise NotImplementedError("TODO")
        # # if we're different types, we're not equal
        # return False

    def __hash__(self) -> int:
        return hash(self.uuid)


class LocalAuthor(Author):
    """An author that is on this node"""

    user: models.OneToOneField[User] = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="author"
    )  # https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model

    def get_stream(
        self, paginate_start: int = 0, paginate_count: Optional[int] = None
    ) -> list[Post]:
        """Get the stream of posts that this author can see

        Args:
            paginate_start (int, optional): returned posts start at this index of the true stream when sorted by newest to oldest. Defaults to 0.
            paginate_end (Optional[int], optional): Get this many posts, or all if None. Defaults to None.

        Returns:
            list[Post]: QuerySet of Post objects that the author is guaranteed to be able to see
        """
        # TODO join the self.private_inbox and the public timeline

        base_query = Q(is_deleted=False)
        following = self.following.all()

        # Visibility types
        public_posts = Q(
            visibility_type=Post.VisibilityTypes.PUBLIC
        )

        unlisted_posts = Q(
            base_author__in=following,
            visibility_type=Post.VisibilityTypes.UNLISTED
        )

        # Get friends (mutual followers)
        friends = [
            author for author in following if self.get_is_friends_with(author)]
        friends_posts = Q(
            base_author__in=friends,
            visibility_type=Post.VisibilityTypes.FRIENDS_ONLY
        )

        # private_inbox = Q(
        #     is_in_private_inbox_of=self
        # )

        query = base_query & (public_posts | unlisted_posts | friends_posts)

        text_posts = PostTextBased.objects.filter(query)

        # Combine and sort all posts
        all_posts: list[Post] = sorted(
            chain(text_posts),
            key=lambda post: post.date_created,
            reverse=True
        )

        # Apply pagination
        if paginate_count is not None:
            all_posts = all_posts[paginate_start:paginate_start + paginate_count]
        elif paginate_start > 0:
            all_posts = all_posts[paginate_start:]

        return all_posts


class RemoteAuthor(Author):
    """An author that is on another node"""

    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    # Eventually will contain extra fields and methods/overrides for authors on other nodes


class FollowRequest(models.Model):
    """A follow request, `actor` wants to follow `target`"""
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        LocalAuthor,
        on_delete=models.CASCADE,
        related_name="follow_requests_requested"
    )
    target = models.ForeignKey(
        LocalAuthor,
        on_delete=models.CASCADE,
        related_name="follow_requests_pending"
    )

    @property
    def actor_username(self) -> str:
        assert isinstance(self.actor, LocalAuthor)
        return self.actor.user.username


class Post(models.Model):
    """
    A post made by an Author, this is an abstract class and should not be instantiated, use one of the subclasses below
    """

    class Meta:
        abstract = True

    # https://docs.djangoproject.com/en/5.1/ref/models/fields/#enumeration-types
    class VisibilityTypes(models.TextChoices):
        PUBLIC = "PU", _("Public")
        UNLISTED = "UN", _("Unlisted")
        FRIENDS_ONLY = "FO", _("Friends-Only")

    # Fields
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    # this is the author of the post, it always returns a base author object (not a subclass)
    # use the author property to get the correct author object
    base_author = models.ForeignKey(
        Author, on_delete=models.PROTECT, blank=True, null=True)
    visibility_type = models.CharField(
        max_length=2, choices=VisibilityTypes.choices, default=VisibilityTypes.PUBLIC
    )
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(
        null=True, default=None
    )  # set to null if never edited

    # Reference: `%(class)s_` from github copilot
    # For non-public posts, this value is used to determine who receives this post
    is_in_private_inbox_of = models.ManyToManyField(
        Author, related_name="%(class)s_private_inbox", blank=True
    )

    # Computed Properties
    @property
    def has_been_edited(self) -> bool:
        return self.date_edited is not None

    @property
    def author(self) -> Author | None:
        """The author of this post"""
        # implementation is a little janky due to Django's inheritance  , but it should work
        if self.base_author is None:
            return None

        if LocalAuthor.objects.filter(uuid=self.base_author.uuid).exists():
            return LocalAuthor.objects.get(uuid=self.base_author.uuid)
        elif RemoteAuthor.objects.filter(uuid=self.base_author.uuid).exists():
            return RemoteAuthor.objects.get(uuid=self.base_author.uuid)
        else:
            raise ValueError("Unknown author type, this should never happen")

    @property
    def css_class(self) -> str:
        raise NotImplementedError(
            "This method must be implemented by a subclass")

    @property
    def like_count(self) -> int:
        return self.get_likes().count()

    # Methods
    def _finalize_edit(self) -> None:
        """Call this after updating a post's content"""
        self.date_edited = timezone.now()
        self.save()

    def check_can_be_seen_by(self, other: Author) -> bool:
        """Returns true if the other author can see this post"""

        if isinstance(other, LocalAuthor) and other.user.is_superuser:
            return True
        if self.is_deleted or self.author is None:
            return False
        if self.author == other:
            return True
        if self.visibility_type == self.VisibilityTypes.PUBLIC:
            return True
        elif self.visibility_type == self.VisibilityTypes.UNLISTED:
            return True
        elif self.visibility_type == self.VisibilityTypes.FRIENDS_ONLY:
            # Friends-only posts visible only to friends
            return self.author.get_is_friends_with(other)
        else:
            raise ValueError(
                f"Unknown visibility type: {self.visibility_type}")

    def send_to_required_private_inboxes(self) -> None:
        """Send this post to the required private inboxes, updates the self.is_in_private_inbox_of field"""
        if self.author is None:
            return None
        for author in self.author.followers.all():
            if self.check_can_be_seen_by(author):
                self.is_in_private_inbox_of.add(author)

    def delete(self, using: Any | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """deletes the Post, overrides django delete. not a permanent delete (not removed from DB)"""
        # just change the variable for soft deletion
        self.is_deleted = True
        self.save()
        return (0, {})

    def _get_differentiators(self) -> QuerySet[PostDifferentiator]:
        """Get all PostDifferentiator objects pointing to this post, Useful for getting likes and comments"""
        raise NotImplementedError(
            "This method must be implemented by a subclass")

    def get_likes(self) -> QuerySet[Like]:
        """Get all likes on this post"""
        found_differentiators = self._get_differentiators()
        return Like.objects.filter(target_post_differentiator__in=found_differentiators)

    def get_comments(self) -> QuerySet[Comment]:
        """Get all comments on this post"""
        found_differentiators = self._get_differentiators()
        return Comment.objects.filter(_post_differentiator__in=found_differentiators)

    def get_absolute_url(self) -> str:
        """Generate the frontend URL in `posts/{POST_UUID}/` format."""

        if self.visibility_type == self.VisibilityTypes.FRIENDS_ONLY:
            raise ValueError("Friends-only posts cannot be shared.")

        return f"{THIS_NODE_URL}/post/{self.uuid}/"


class PostTextBased(Post):
    """
    A post that contains text
    """

    class TextPostTypes(models.TextChoices):
        PLAINTEXT = "PT", _("Plain Text")
        MARKDOWN = "MD", _("Markdown")

    # Fields
    content = models.TextField()
    post_type = models.CharField(
        max_length=2, choices=TextPostTypes.choices, default=TextPostTypes.PLAINTEXT
    )

    @property
    def css_class(self) -> str:
        if self.post_type == self.TextPostTypes.PLAINTEXT:
            return "post-plaintext"
        elif self.post_type == self.TextPostTypes.MARKDOWN:
            return "post-markdown"
        else:
            raise ValueError(f"Unknown post type: {self.post_type}")

    def edit(self, new_content: str) -> None:
        """Edit the content of this post"""
        self.content = new_content
        self._finalize_edit()

    def convert_type(self, new_type: TextPostTypes) -> None:
        """Convert this post to a different type"""
        self.post_type = new_type
        self._finalize_edit()

    def _get_differentiators(self) -> QuerySet[PostDifferentiator]:
        """Get all PostDifferentiator objects pointing to this post, useful for getting likes and comments"""
        return PostDifferentiator.objects.filter(_post_text=self)


class PostMediaBased(Post):
    """
    A post that contains an image
    TODO consider whether multiple classes or an enum field are better for video vs images
    """

    def _get_differentiators(self) -> QuerySet[PostDifferentiator]:
        """Get all PostDifferentiator objects pointing to this post, useful for getting likes and comments"""
        return PostDifferentiator.objects.filter(_post_media=self)


class PostDifferentiator(models.Model):
    """A model that links to exactly one post subclass, used as a ForeignKey"""
    _post_text = models.ForeignKey(
        PostTextBased, on_delete=models.CASCADE, blank=True, null=True)
    _post_media = models.ForeignKey(
        PostMediaBased, on_delete=models.CASCADE, blank=True, null=True)

    # if you add a post type, add it to the `fields` list too :)
    FIELDS = ["_post_text", "_post_media"]

    @classmethod
    def get_post_by_uuid(cls, uuid: uuid.UUID) -> Post:
        """Get a post by its UUID"""
        if PostTextBased.objects.filter(uuid=uuid).exists():
            return PostTextBased.objects.get(uuid=uuid)
        elif PostMediaBased.objects.filter(uuid=uuid).exists():
            return PostMediaBased.objects.get(uuid=uuid)
        else:
            raise Post.DoesNotExist("Post not found")

    @staticmethod
    def create_differentiator_for_post(post: Post) -> PostDifferentiator:
        if isinstance(post, PostTextBased):
            return PostDifferentiator.objects.create(_post_text=post)
        elif isinstance(post, PostMediaBased):
            return PostDifferentiator.objects.create(_post_media=post)
        else:
            raise ValueError("Unsupported post type")

    @property
    def post(self) -> Post:
        if self._post_text:
            return self._post_text
        elif self._post_media:
            return self._post_media
        else:
            raise ValueError("This post differentiator has no post")

    def clean(self) -> None:
        num_set = sum(
            [getattr(self, field) is not None for field in self.FIELDS])
        if num_set != 1:
            raise ValidationError("Exactly one post field must be set")
        return super().clean()


class HostedImage(models.Model):
    """
    Stores an uploaded image along with an optional title.
    """
    title: models.CharField["HostedImage", str] = models.CharField(
        max_length=255,
        blank=True
    )
    image: models.ImageField = models.ImageField(
        upload_to="hosted_images/"
    )
    uploaded_at: models.DateTimeField["HostedImage", datetime] = models.DateTimeField(
        auto_now_add=True
    )

    objects: models.Manager["HostedImage"] = models.Manager()

    def __str__(self) -> str:
        return self.title or str(self.image.name)


class Comment(models.Model):
    """A comment on a post"""
    # Serializer: api.serializers.comment_serializers.CommentSerializer
    class CommentTypes(models.TextChoices):
        PLAINTEXT = "PT", _("Plain Text")
        MARKDOWN = "MD", _("Markdown")

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    author: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_type = models.CharField(
        max_length=2, choices=CommentTypes.choices, default=CommentTypes.PLAINTEXT
    )
    _post_differentiator: models.ForeignKey[PostDifferentiator, PostDifferentiator] = models.ForeignKey(
        PostDifferentiator, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def post(self) -> Post:
        return self._post_differentiator.post

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self._post_differentiator}"

    def check_can_be_seen_by(self, other: Author) -> bool:
        """Returns true if the other author can see this comment
        As an author, comments on my friends-only posts are visible only to my friends and the comment's author."""
        # ? how could a comment be made on a post that the author can't see?
        if self.post.check_can_be_seen_by(other):
            return True
        if self.author == other:
            return True
        return False

    def get_likes(self) -> QuerySet[Like]:
        """Get all likes on this comment"""
        return Like.objects.filter(target_comment=self)


class Like(models.Model):

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    author: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    target_post_differentiator: models.ForeignKey[PostDifferentiator, Optional[PostDifferentiator]] = models.ForeignKey(
        PostDifferentiator, on_delete=models.CASCADE, blank=True, null=True)
    target_comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, blank=True, null=True)
    # target_comment and target_post should not both be null
    # target_comment and target_post should not both be set

    def clean(self) -> None:
        if self.target_comment is None and self.target_post_differentiator is None:
            raise ValidationError(
                _("Like must target a comment or post"))
        if self.target_comment is not None and self.target_post_differentiator is not None:
            raise ValidationError(
                _("Like must target a comment or post, not both"))
        return super().clean()

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def target(self) -> Post | Comment:
        if self.target_comment:
            return self.target_comment
        elif self.target_post_differentiator:
            return self.target_post_differentiator.post
        else:
            raise ValueError(
                "This like has no target, this should never happen")

    def get_id_url(self, prepend_host: bool = True) -> str:
        url = reverse("api:liked_author_specific_like",
                      args=[self.author.uuid, self.uuid])
        if prepend_host:
            return f"{THIS_NODE_URL}{url}"
        return url

    def get_target_url(self, prepend_host: bool = True) -> str:
        if isinstance(self.target, Post):
            url = reverse("api:post_author_specific", args=[
                getattr(self.target.author, "uuid", None), self.target.uuid])
        elif isinstance(self.target, Comment):
            url = reverse("api:comments_serial", args=[
                self.target.post.uuid, self.target.uuid])
        else:
            raise ValueError("Unknown target type")
        if prepend_host:
            return f"{THIS_NODE_URL}{url}"
        return url

    def __str__(self) -> str:
        return f"Like by {self.author} on {self.target}"
