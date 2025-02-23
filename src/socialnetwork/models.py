from __future__ import annotations
import uuid
from typing import Any

from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from typing import Optional
from django.contrib.auth.models import User

from django.db.models import Q
from itertools import chain


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
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    bio = models.TextField(blank=True)
    
    # Computed Properties
    @property
    def followers(self) -> models.QuerySet[Author]:
        return Author.objects.filter(following=self)
    
    @property
    def username(self) -> str:
        raise NotImplementedError("This method must be implemented by a subclass")
    
    
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
    
    def delete(self, *args:Any, **kwargs:Any) -> tuple[int, dict[str, int]]:
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
    
class LocalAuthor(Author):
    """An author that is on this node"""

    user:models.OneToOneField[User] = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="author"
    )  # https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
    
    @property
    def username(self) -> str:
        return self.user.username

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
        public_posts = Q(visibility_type=Post.VisibilityTypes.PUBLIC)
        
        private_inbox = Q(
            is_in_private_inbox_of=self
        )

        query = base_query & (public_posts | private_inbox)
        
        text_posts = PostTextBased.objects.filter(query)
        
        # Combine and sort all posts
        all_posts:list[Post] = sorted(
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
    remote_username = models.CharField(max_length=50)
    
    @property
    def username(self) -> str:
        return self.remote_username
    # Eventually will contain extra fields and methods/overrides for authors on other nodes


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
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # this is the author of the post, it always returns a base author object (not a subclass)
    # use the author property to get the correct author object
    base_author = models.ForeignKey(Author, on_delete=models.PROTECT, blank=True, null=True) 
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
    def author(self) -> Author|None:
        """The author of this post"""
        fetched_author:Author|None = self.base_author
        if fetched_author is None:
            return None
        fetched_uuid = fetched_author.uuid

        if LocalAuthor.objects.filter(uuid=fetched_uuid).exists():
            return LocalAuthor.objects.get(uuid=fetched_uuid)
        elif RemoteAuthor.objects.filter(uuid=fetched_uuid).exists():
            return RemoteAuthor.objects.get(uuid=fetched_uuid)
        else:
            raise ValueError(f"Unknown author type: {fetched_author}")
        
    @property
    def css_class(self) -> str:
        raise NotImplementedError("This method must be implemented by a subclass")

    # Methods
    def _finalize_edit(self) -> None:
        """Call this after updating a post's content"""
        self.date_edited = timezone.now()
        self.save()
    def _check_can_be_seen_by(self, other: Author) -> bool:
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
            return False
        elif self.visibility_type == self.VisibilityTypes.FRIENDS_ONLY:
            return self.author.get_is_friends_with(other)
        else:
            raise ValueError(f"Unknown visibility type: {self.visibility_type}")

    def send_to_required_private_inboxes(self) -> None:
        """Send this post to the required private inboxes, updates the self.is_in_private_inbox_of field"""
        if self.author is None:
            return None
        for author in self.author.followers.all():
            if self._check_can_be_seen_by(author):
                self.is_in_private_inbox_of.add(author)

    def delete(self, using: Any | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """deletes the Post, overrides django delete. not a permanent delete (not removed from DB)"""
        #just change the variable for soft deletion
        self.is_deleted = True 
        self.save()
        return (0, {})


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


class PostMediaBased(Post):
    """
    A post that contains an image
    TODO consider whether multiple classes or an enum field are better for video vs images
    """

    pass  # TODO



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