from __future__ import annotations

from typing import Any, Collection, Optional, TYPE_CHECKING, cast
if TYPE_CHECKING:
    from django.db.models import QuerySet
    from posts.models import Post
    from comments.models import Comment
    from likes.models import Like

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager

from core.utils.api_object import ApiObject, ApiObjectManager

# =============================================================================
# Users
# =============================================================================


class UserManagerBase(UserManager["User"]):
    def get_user(self, username: str) -> User:
        return self.get(username=username)


class ExternalNodeUserManager(UserManagerBase):
    """This manager is for the django users that represent external nodes
    External nodes authenticate with the system using these users"""

    def get_queryset(self) -> models.QuerySet[User]:
        return super().get_queryset().filter(type=User.Types.NODE)

    def create_user(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields: Any) -> User:
        return super().create_user(username, email, password, type=User.Types.NODE, **extra_fields)

    def create_superuser(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields: Any) -> User:
        raise ValidationError("Cannot create superuser for external node")


class AuthorUserManager(UserManagerBase):
    """Manages users that are linked to authors"""

    def get_queryset(self) -> models.QuerySet[User]:
        return super().get_queryset().filter(type=User.Types.AUTHOR)

    def create_user(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields: Any) -> User:
        return super().create_user(username, email, password, type=User.Types.AUTHOR, **extra_fields)

    def create_superuser(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields: Any) -> User:
        # do it via a join request
        if User.objects.filter(username=username).exists() or JoinRequest.objects.filter(username=username).exists():
            raise ValidationError(f"Username {username} is already taken")
        if User.objects.filter(email=email).exists() or JoinRequest.objects.filter(email=email).exists():
            raise ValidationError(f"Email {email} is already taken")
        if password is None:
            raise ValidationError("Password is required")
        request = JoinRequest.objects.create(
            username=username,
            email=email,
            display_name=username,
            password=password
        )
        author = request.approve()
        assert author._user is not None
        author._user.is_superuser = True
        author._user.is_staff = True
        author._user.save()
        return author._user


class User(AbstractUser):
    """Base user model for all users in the system"""

    class Types(models.TextChoices):
        """Types of User"""
        AUTHOR = "Author", _("Author")
        NODE = "Node", _("Node")

    type = models.CharField(
        _("User Type"), max_length=6, choices=Types.choices, blank=False, null=False)
    email = models.EmailField(_("Email Address"), blank=True)

    # managers, `objects` might not be available, but it shouldn't be used anyway
    authors = AuthorUserManager()
    nodes = ExternalNodeUserManager()


# =============================================================================
# Authors
# =============================================================================

class AuthorManager(ApiObjectManager["Author"]):
    def find_authors(self, username: str) -> models.QuerySet[Author]:
        return self.filter(username=username)


class LocalAuthorManager(AuthorManager):
    """Custom manager for Local Author model"""

    def get_queryset(self) -> models.QuerySet[LocalAuthor]:
        return cast(models.QuerySet[LocalAuthor], super().get_queryset().filter(_user__isnull=False))

    def get(self, *args: Any, **kwargs: Any) -> LocalAuthor:
        return cast(LocalAuthor, super().get(*args, **kwargs))

    def create(self, *args: Any, **kwargs: Any) -> LocalAuthor:
        """
        Create a new local author
        Raises ValidationError if user is not provided
        """
        if "_user" not in kwargs:
            raise ValidationError(
                "Local authors must have a user account, consider creating a JoinRequest and approving it instead")
        return cast(LocalAuthor, super().create(*args, **kwargs))

    def create_author(self,  username: str, password: str, email: Optional[str] = None, display_name: Optional[str] = None, is_superuser: bool = False) -> LocalAuthor:
        """Create a local author (this will happen by creating and automatically approving a join request)"""
        join_request = JoinRequest.objects.create_join_request(
            username, password, email, display_name)
        author = join_request.approve()
        if is_superuser:
            author.user.is_superuser = True
            author.user.is_staff = True
            author.user.save()
        return author

    def find_author_with_user(self, user: User) -> Optional[LocalAuthor]:
        """Find a local author with the given user (may be none)"""
        return self.get_queryset().filter(_user=user).first()


class ExternalAuthorManager(AuthorManager):
    """Custom manager for External Author model"""

    def get_queryset(self) -> models.QuerySet[Author]:
        return super().get_queryset().filter(_user__isnull=True)

    def get(self, *args: Any, **kwargs: Any) -> ExternalAuthor:
        return cast(ExternalAuthor, super().get(*args, **kwargs))

    def create(self, *args: Any, **kwargs: Any) -> ExternalAuthor:
        """
        Create a new external author
        Raises ValidationError if user is provided
        """
        if "_user" in kwargs:
            raise ValidationError("External authors cannot have a user account")
        return cast(ExternalAuthor, super().create(*args, **kwargs))


class Author(ApiObject):
    """Author model for both local and external authors"""

    class Meta:
        ordering = ["uuid"]

    # unique=False because we have external authors, which can have the same username as a local one (fqid is the unique identifier)
    username: models.CharField[str, str] = models.CharField(
        _("Username"), max_length=255, unique=False, blank=True)
    display_name = models.CharField(_("Display Name"), max_length=255)
    bio = models.TextField(_("Bio"), blank=True)
    profile_image = models.URLField(_("Profile Image"), blank=True)
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers', blank=True)

    page_url = models.URLField(_("Page URL"), blank=True)
    # external authors will not have a user account
    _user: models.OneToOneField[User, Optional[User]] = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    # managers
    objects: AuthorManager = AuthorManager()
    local_authors = LocalAuthorManager()
    external_authors = ExternalAuthorManager()

    # type hints for reverse relations (you can use author.posts/author.comments to get all posts/comments by the author, etc)
    if TYPE_CHECKING:
        posts: QuerySet[Post]
        comments: QuerySet[Comment]
        likes: QuerySet[Like]
        follow_requests_sent: QuerySet[FollowRequest]
        follow_requests_received: QuerySet[FollowRequest]
        followers: QuerySet[Author]

    # properties
    @property
    def is_external(self) -> bool:
        return self._user is None

    @property
    def is_local(self) -> bool:
        return not self.is_external

    @property
    def user(self) -> Optional[User]:
        return self._user

    def clean(self) -> None:
        super().clean()
        # make sure that the fqid starts with the host
        if not self.fqid.startswith(self.host_node.host_url):
            raise ValidationError(
                f"FQID must start with the host, ({self.fqid} does not start with {self.host_node})")
        if self.is_local:
            if self._user is None:
                raise ValidationError("Local authors must have a user account")
            if self._user.username != self.username:
                if User.objects.filter(username=self.username).exists():
                    raise ValidationError(
                        f"Username {self.username} is already taken, cannot change it")
                self._user.username = self.username
                self._user.save()
            if not self.page_url:
                self.page_url = self.generate_page_url()  # might be a little hacky, but it'll work

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        if self._user is not None:
            self._user.delete()
        return super().delete(using, keep_parents)

    def __str__(self) -> str:
        location = "External" if self.is_external else "Local"
        return f"{self.display_name} ({location})"

    def generate_fqid(self) -> str:
        # TODO replace with reverse() call :)
        return f"{self.host_node.host_url}/authors/{self.uuid}"

    def generate_page_url(self) -> str:
        # TODO replace with reverse() call :)
        return f"{self.host_node.host_url}/authors/{self.uuid}"

    def get_stream(self, paginate_start: int, paginate_count: int) -> QuerySet[Post]:
        """Get the stream of posts for this author

        Returns:
            QuerySet[Post]: All posts in this author's stream
        """
        # Do not modify this function, modify the get_posts_in_stream_of_author method instead
        return Post.visible_posts.get_posts_in_stream_of_author(self, paginate_start=paginate_start, paginate_count=paginate_count)

# === Proxy Classes for Authors ===


class LocalAuthor(Author):
    class Meta:
        proxy = True

    @property
    def user(self) -> User:
        if self._user is None:
            raise ValidationError(
                "Local authors must have a user account, this should never happen")
        return self._user


class ExternalAuthor(Author):
    class Meta:
        proxy = True

    @property
    def user(self) -> None:
        if self._user is not None:
            raise ValidationError(
                "External authors cannot have a user account, this should never happen")
        return None

# =============================================================================
# Follow Requests
# =============================================================================


class FollowRequestManager(ApiObjectManager["FollowRequest"]):
    def create_follow_request(self, follower: Author, followee: Author) -> FollowRequest:
        """Create a new follow request"""
        host_node = followee.host_node
        return self.create(follower=follower, followee=followee, host_node=host_node)

    def get_follow_request(self, follower: Author, followee: Author) -> FollowRequest:
        """Get a follow request if it exists, raises DoesNotExist if it doesn't"""
        return self.get(follower=follower, followee=followee)

    def check_exists(self, follower: Author, followee: Author) -> bool:
        return self.get_follow_request(follower, followee) is not None


class FollowRequest(ApiObject):
    """A request for author `follower` to follow author `followee`"""
    follower: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, related_name="follow_requests_sent", on_delete=models.CASCADE)
    followee: models.ForeignKey[Author, Author] = models.ForeignKey(
        Author, related_name="follow_requests_received", on_delete=models.CASCADE)

    objects: FollowRequestManager = FollowRequestManager()

# =============================================================================
# External Nodes
# =============================================================================


class NodeManager(models.Manager["Node"]):
    def create(self, *args: Any, **kwargs: Any) -> Node:
        """
        Create a new node
        Raises ValidationError if is_local_node=True and there is already a local node
        """
        if "is_local_node" in kwargs and kwargs["is_local_node"]:
            if Node.objects.filter(is_local_node=True).exists():
                raise ValidationError("There can only be one local node")
        return super().create(*args, **kwargs)

    def get_local_node(self) -> Node:
        """Gets the local node, or creates one if it doesn't exist"""
        try:
            return super().get_queryset().get(is_local_node=True)
        except Node.DoesNotExist:
            from core.settings import SITE_URL
            return self.create(
                name="self",
                host_url=f"{SITE_URL}/",
                is_local_node=True
            )


class ExternalNodeManager(NodeManager):
    def get_queryset(self) -> models.QuerySet[Node]:
        return super().get_queryset().filter(is_local_node=False)

    def create(self, *args: Any, **kwargs: Any) -> Node:
        return super().create(*args, is_local_node=False, **kwargs)

    def create_node(self, name: str, host_url: str) -> Node:
        return self.create(name=name, host_url=host_url)

    def find_node(self, host_url: str) -> Optional[Node]:
        return self.filter(host_url=host_url).first()


class Node(models.Model):
    """
    A Node is an instance of an API-compatible system to ours
    The host system is represented as the only node with `is_local_node=True`
    """

    uuid: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        _("UUID"), primary_key=True, editable=False, default=uuid.uuid4)
    name: models.CharField[str, str] = models.CharField(_("Name"), max_length=255)
    host_url: models.URLField[str, str] = models.URLField(_("Host"), unique=True)

    # internal_user is for authentication - this may change in the future
    internal_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # if true, this `Node` is the local node. This can only be true for one node (upheld in the manager)
    is_local_node = models.BooleanField(_("Is Local Node"), default=False)

    # managers
    objects: NodeManager = NodeManager()
    external_nodes: ExternalNodeManager = ExternalNodeManager()

    def __str__(self) -> str:
        prefix = "[Local] " if self.is_local_node else ""
        return f"{prefix}{self.name} ({self.host_url})"

    def get_hosted_users(self) -> models.QuerySet[Author]:
        return Author.objects.filter(host_node=self)


# =============================================================================
# Join requests
# =============================================================================
class JoinRequestManager(models.Manager["JoinRequest"]):
    def create(self, *args: Any, **kwargs: Any) -> JoinRequest:
        """
        Create a new join request
        Raises ValidationError if username or email is already taken
        """
        if User.objects.filter(username=kwargs["username"]).exists():
            raise ValidationError(f"Username {kwargs['username']} is already taken")
        if kwargs.get("email", None) and User.objects.filter(email=kwargs["email"]).exists():
            raise ValidationError(f"Email {kwargs['email']} is already taken")
        return super().create(*args, **kwargs)

    def create_join_request(self, username: str, password: str, email: Optional[str] = None, display_name: Optional[str] = None) -> JoinRequest:
        """Create a new join request, returns the created request. If display_name is None, it will be set to username"""
        if display_name is None:
            display_name = username
        return self.create(username=username, email=email, display_name=display_name, password=password)

    def get_join_request(self, username: str) -> JoinRequest:
        return self.get(username=username)


class JoinRequest(models.Model):
    """A request to join the system as a local author (requires admin approval)"""

    uuid = models.UUIDField(_("UUID"), primary_key=True, editable=False, default=uuid.uuid4)
    username = models.CharField(_("Username"), max_length=255, unique=True)
    email = models.EmailField(_("Email Address"), blank=True, null=True, unique=True)
    display_name = models.CharField(_("Display Name"), max_length=255)
    password = models.CharField(_("Password"), max_length=255)
    is_denied = models.BooleanField(_("Is Denied"), default=False)

    # managers
    objects: JoinRequestManager = JoinRequestManager()

    def __str__(self) -> str:
        return f"{self.display_name} ({self.username})"

    def approve(self) -> LocalAuthor:
        """Approve the join request and create a new local author
        raises ValidationError if username is already taken
        raises ValidationError if the request was denied
        """
        if self.is_denied:
            raise ValidationError("This request is denied, you need to undeny it before approving")

        node: Node = Node.objects.get_local_node()

        # make sure username isn't taken already
        if Author.objects.filter(username=self.username).exists():
            raise ValidationError(f"Username {self.username} is already taken")

        # create the new local user
        user = User.authors.create_user(self.username, self.email, self.password)
        try:
            author = Author.local_authors.create(
                username=self.username,
                display_name=self.display_name,
                host_node=node,
                _user=user
            )
            self.force_delete()
            return author
        except Exception as e:
            user.delete()
            raise e

    def deny(self) -> None:
        """Deny the join request
        Raises ValidationError if the request is already denied
        """
        if self.is_denied:
            raise ValidationError("Cannot deny a request that is already denied")
        self.is_denied = True
        self.save()

    def undeny(self) -> None:
        """Undeny the join request
        Raises ValidationError if the request is not denied
        """
        if not self.is_denied:
            raise ValidationError("Cannot undeny a request that is not denied")
        self.is_denied = False
        self.save()

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Delete the join request
        Raises ValidationError if the request is denied
        """
        if self.is_denied:
            return super().delete(*args, **kwargs)
        else:
            raise ValidationError("Cannot delete a non-denied request")

    def force_delete(self) -> tuple[int, dict[str, int]]:
        """Delete the join request regardless of its status"""
        return super().delete()

    def clean(self, exclude: Optional[Collection[str]] = None) -> None:
        if JoinRequest.objects.filter(username=self.username).exists():
            raise ValidationError(
                {"username": _(f"Username '{self.username}' has already requested to join.")})
        if User.objects.filter(username=self.username).exists():
            raise ValidationError({"username": _(f"Username '{self.username}' is already taken.")})
        if self.email:
            if JoinRequest.objects.filter(email=self.email).exists():
                raise ValidationError(
                    {"username": _(f"Email '{self.email}' has already requested to join.")})
            if User.objects.filter(email=self.email).exists():
                raise ValidationError({"email": _(f"Email '{self.email}' is already taken.")})
