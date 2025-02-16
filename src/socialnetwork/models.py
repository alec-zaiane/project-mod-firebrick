from __future__ import annotations
from django.db import models
import uuid
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from typing import Optional
from django.contrib.auth.models import User

class RemoteNode(models.Model):
    #TODO will contain fields for the remote nodes that this instance knows about
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
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    username = models.CharField(max_length=50)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    
    # Type Hints *these are not model fields*
    following: models.ManyToManyField[Author,Author]
    
    # Computed Properties
    @property
    def followers(self):
        return Author.objects.filter(following=self)
    
    # Methods
    def __init__(self):
        if self.__class__ == Author:
            # Abstract-ness is a bit janky due to Django's ORM (cannot make Foreign Keys with an abstract class), this is a workaround
            raise TypeError("Author is an abstract class and cannot be instantiated")
    
    def get_is_friends_with(self, other: Author) -> bool:
        """Returns true if this author is friends with the other author"""
        return self in other.following and other in self.following
    
class LocalAuthor(Author):
    """An author that is on this node"""
    auth_user = models.OneToOneField(User, on_delete=models.PROTECT) # see https://docs.djangoproject.com/en/5.1/topics/auth/default/
    def get_stream(self, paginate_start:int=0, paginate_count:Optional[int]=None) -> models.QuerySet[Post]:
        """Get the stream of posts that this author can see

        Args:
            paginate_start (int, optional): returned posts start at this index of the true stream when sorted by newest to oldest. Defaults to 0.
            paginate_end (Optional[int], optional): Get this many posts, or all if None. Defaults to None.

        Returns:
            models.QuerySet[Post]: QuerySet of Post objects that the author is guaranteed to be able to see
        """
        #TODO join the self.private_inbox and the public timeline
        raise NotImplementedError()
    
class RemoteAuthor(Author):
    """An author that is on another node"""
    pass # Eventually will contain extra fields and methods/overrides for authors on other nodes
    
    
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
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    visibility_type = models.CharField(max_length=2, choices=VisibilityTypes.choices, default=VisibilityTypes.PUBLIC)
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(null=True, default=None) # set to null if never edited
    
    # Reference: `%(class)s_` from github copilot
    # For non-public posts, this value is used to determine who receives this post
    is_in_private_inbox_of = models.ManyToManyField(Author, related_name='%(class)s_private_inbox', blank=True)
    
    # Type Hints *these are not model fields*
    is_in_private_inbox_of:models.ManyToManyField["Post",Author]
    
    # Computed Properties
    @property
    def has_been_edited(self):
        return self.date_edited is not None
    
    # Methods
    def _finalize_edit(self):
        """Call this after updating a post's content"""
        self.date_edited = timezone.now()
        self.save()
    
    def _check_can_be_seen_by(self, other: Author) -> bool:
        """Returns true if the other author can see this post"""
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
        for author in self.author.followers.all():
            if self._check_can_be_seen_by(author):
                self.is_in_private_inbox_of.add(author)
        

class PostPlainText(Post):
    """
    A post that contains only plain text
    """
    # Fields
    content = models.TextField()
    
    def edit(self, new_content: str):
        """Edit the content of this post"""
        self.content = new_content
        self._finalize_edit()
        
class PostMarkdown(Post):
    """
    A post that contains markdown
    """
    # Fields
    content = models.TextField()
    
    def edit(self, new_content: str):
        """Edit the content of this post"""
        self.content = new_content
        self._finalize_edit()
        
class PostImage(Post):
    """
    A post that contains an image
    """
    pass #TODO

