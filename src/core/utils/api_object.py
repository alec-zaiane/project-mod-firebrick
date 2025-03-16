"""All models (Author, Post, etc.) that are passed between nodes should inherit from this class

Gives the model a UUID, host node, and FQID (fully qualified ID)"""

from typing import TYPE_CHECKING, Any, TypeVar, Generic
from datetime import datetime

if TYPE_CHECKING:
    from user_management.models import Node, Author

from uuid import UUID, uuid4

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ModelT = TypeVar("ModelT", bound="ApiObject")


class ApiObjectManager(models.Manager[ModelT], Generic[ModelT]):
    def create(self, *args: Any, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        instance.save(force_insert=True)
        return instance

    def get_by_fqid(self, fqid: str) -> ModelT:
        return self.get(fqid=fqid)


class ApiObject(models.Model):
    class Meta:
        abstract = True
    # This is the LOCAL UUID (if node1.author1's uuid is 123, node2's copy of author1 will have a different uuid)
    # Use the fqid to identify the object across nodes
    uuid: models.UUIDField[UUID, UUID] = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid4, editable=False)

    host_node: models.ForeignKey["Node", "Node"] = models.ForeignKey(
        'user_management.Node', on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_related")
    fqid: models.CharField[str, str] = models.CharField(
        _("FQID"), max_length=255, unique=True, blank=True)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        _("Created at"), auto_now_add=True)
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        _("Edited at"), auto_now=True)

    @property
    def is_updated(self) -> bool:
        """Whether or not this object has been updated since it was created"""
        return self.created_at != self.updated_at

    def generate_fqid(self) -> str:
        # Ideally this would be an abstract method, but Django shenanigans
        # MUST BE DETERMINISTIC
        raise NotImplementedError(
            f"generate_fqid must be implemented by subclasses (perhaps in `{self.__class__}`?)")

    def clean(self) -> None:
        super().clean()
        if not self.fqid:
            self.fqid = self.generate_fqid()
        elif not self.fqid.startswith(self.host_node.host_url):
            raise ValidationError(f"fqid must start with the host node's host url, got {self.fqid}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class AuthoredApiObject(ApiObject):
    """An API object with an author attribute
    This class does not define the author attribute, it is up to subclasses to define it (because of reverse relation naming)
    """
    class Meta:
        abstract = True

    if TYPE_CHECKING:
        author: models.ForeignKey["Author", "Author"]
