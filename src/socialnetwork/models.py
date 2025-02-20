from __future__ import annotations
import uuid
from typing import Any

from django.db import models
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
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    
    # Computed Properties
    @property
    def followers(self) -> models.QuerySet[Author]:
        return Author.objects.filter(following=self)
    
    # Methods
    
    def get_is_friends_with(self, other: Author) -> bool:
        """Returns true if this author is friends with the other author"""
        self_is_following_other = other.following.filter(pk=self.pk).exists()
        other_is_following_self = self.following.filter(pk=other.pk).exists()
        return self_is_following_other and other_is_following_self
    
class LocalAuthor(Author):
    """An author that is on this node"""
    user = models.OneToOneField(User, on_delete=models.CASCADE) # https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
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
    
    def delete(self, using:Any=..., keep_parents:bool=...): # type: ignore # not sure why the default keep_parents value is Ellipsis, clashes with bool type
        """Delete this author"""
        self.user.delete()
        return super().delete(using, keep_parents)
    
class RemoteAuthor(Author):
    """An author that is on another node"""
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    username = models.CharField(max_length=50)
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
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    visibility_type = models.CharField(max_length=2, choices=VisibilityTypes.choices, default=VisibilityTypes.PUBLIC)
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(null=True, default=None) # set to null if never edited
    
    # Reference: `%(class)s_` from github copilot
    # For non-public posts, this value is used to determine who receives this post
    is_in_private_inbox_of = models.ManyToManyField(Author, related_name='%(class)s_private_inbox', blank=True)
    
    
    # Computed Properties
    @property
    def has_been_edited(self) -> bool:
        return self.date_edited is not None
    
    # Methods
    def _finalize_edit(self) -> None:
        """Call this after updating a post's content"""
        self.date_edited = timezone.now()
        self.save()
    
    def _check_can_be_seen_by(self, other: Author) -> bool:
        """Returns true if the other author can see this post"""
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
        for author in self.author.followers.all():
            if self._check_can_be_seen_by(author):
                self.is_in_private_inbox_of.add(author)
        
class PostTextBased(Post):
    """
    A post that contains text
    """
    class TextPostTypes(models.TextChoices):
        PLAINTEXT = "PT", _("Plain Text")
        MARKDOWN = "MD", _("Markdown")
    
    # Fields
    content = models.TextField()
    post_type = models.CharField(max_length=2, choices=TextPostTypes.choices, default=TextPostTypes.PLAINTEXT)
    
    def edit(self, new_content: str):
        """Edit the content of this post"""
        self.content = new_content
        self._finalize_edit()
        
    def convert_type(self, new_type: TextPostTypes):
        """Convert this post to a different type"""
        self.post_type = new_type
        self._finalize_edit()
        
class PostMediaBased(Post):
    """
    A post that contains an image 
    TODO consider whether multiple classes or an enum field are better for video vs images
    """
    pass #TODO

