from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

from socialnetwork.models import LocalAuthor

class AuthorJoinRequest(models.Model):
    """A request to join the nod
    Approved requests are deleted, denied requests are kept
    A request is denied if the `date_denied` field is not null
    """    
    date_requested = models.DateTimeField(auto_now_add=True)
    date_denied = models.DateTimeField(null=True) # if null, request is pending
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    
    @property
    def is_denied(self) -> bool:
        return self.date_denied is not None

    @property
    def css_status(self) -> str:
        return "denied" if self.is_denied else "pending"
    
    def get_validity_errors(self) -> list[str]:
        """ returns a list of errors with the request, or an empty list if the request is valid

        Returns:
            list[str]: Any errors with the request
        """        
        errors:list[str] = []
        if not self.username or not self.password:
            return ["Username and password must be non-empty"]
        if User.objects.filter(username=self.username).exists():
            errors.append("Username already exists")
        return errors
    
    def approve_and_create(self) -> LocalAuthor:
        """Approve this request and create the user
        
        Raises:
            ValueError: If the request is invalid
            
        Returns:
            LocalAuthor: The created author
        """
        if self.get_validity_errors():
            raise ValueError(f"Request is invalid: {self.get_validity_errors()}")
        user = User.objects.create_user(username=self.username, password=self.password)
        author = LocalAuthor()
        author.user = user
        author.save()
        self.delete()
        return author
    
    def deny(self) -> None:
        """Deny this request"""
        self.date_denied = timezone.now()
        self.save()
        
    def undeny(self) -> None:
        """Un-deny this request in case of a mistake"""
        self.date_denied = None
        self.save()

class HostedImage(models.Model):
    """
    Stores an uploaded image along with an optional title.
    """

    # The first type parameter is the model name as a string ("HostedImage"),
    # the second is the Python type the field holds (usually str).
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

    # Explicitly declare the objects manager so Mypy recognizes it
    objects: models.Manager["HostedImage"] = models.Manager()

    def __str__(self) -> str:
        return self.title or str(self.image.name)