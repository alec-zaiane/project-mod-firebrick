from __future__ import annotations
from django.db import models
import uuid
from django.utils import timezone

# Create your models here.


class Author(models.Model):
    """
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
    def get_is_friends_with(self, other: Author) -> bool:
        """Returns true if this author is friends with the other author"""
        return self in other.following and other in self.following
    
class RemoteAuthor(Author):
    pass # Eventually will contain extra fields and method overrides for authors on other nodes
    
    
class Post(models.Model):
    """
    A post made by an Author, this is an abstract class and should not be instantiated, use one of the subclasses below
    """
    class Meta:
        abstract = True
    
    # Fields
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    visibility_type = models.TextChoices("Public", "Unlisted", "Friends-Only")
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(null=True, default=None) # set to null if never edited
    
    # Computed Properties
    @property
    def has_been_edited(self):
        return self.date_edited is not None
    
    # Methods
    def _finalize_edit(self):
        """Call this after updating a post's content"""
        self.date_edited = timezone.now()
        self.save()

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

