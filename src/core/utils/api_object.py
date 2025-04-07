"""All models (Author, Post, etc.) that are passed between nodes should inherit from this class

Gives the model a UUID, host node, and FQID (fully qualified ID)"""

from typing import TYPE_CHECKING, Any, TypeVar, Generic, Optional
from datetime import datetime
from urllib.parse import unquote, quote

if TYPE_CHECKING:
    from user_management.models import Node, Author

from uuid import UUID, uuid4

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ModelT = TypeVar("ModelT", bound="ApiObject")

# Signal structure from ChatGPT: "I want to implement signals on a django abstract class, what is the best way to do this?"
# model: o3-mini, date: 2025-03-23, reasoning: enabled


class ApiObjectManager(models.Manager[ModelT], Generic[ModelT]):
    def create(self, *args: Any, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        instance.save(force_insert=True)
        return instance

    def get_by_fqid(self, fqid: str) -> ModelT:
        return self.get(fqid=fqid)

    def find_by_fqid(self, fqid: str) -> Optional[ModelT]:
        no_slash = self.filter(fqid=fqid).first()
        has_slash = self.filter(fqid=f"{fqid}/").first()
        return no_slash or has_slash

    def find_by_encoded_fqid(self, fqid: str) -> Optional[ModelT]:
        """Find by a percent-encoded fqid"""
        return self.find_by_fqid(unquote(fqid))

    def find_by_uuid(self, uuid: str | UUID) -> Optional[ModelT]:
        return self.filter(uuid=uuid).first()


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
        # so long as the times are within 1ms of each other, consider them equal
        return abs(self.updated_at.timestamp() - self.created_at.timestamp()) > 1e-3

    def generate_fqid(self) -> str:
        # Ideally this would be an abstract method, but Django shenanigans
        # MUST BE DETERMINISTIC
        raise NotImplementedError(
            f"generate_fqid must be implemented by subclasses (perhaps in `{self.__class__}`?)")

    def get_encoded_fqid(self) -> str:
        """Get a percent-encoded fqid"""
        return quote(self.fqid, safe="")

    def clean(self) -> None:
        super().clean()
        if not self.fqid:
            self.fqid = self.generate_fqid()
        elif not self.fqid.startswith(self.host_node.host_url):
            raise ValidationError(f"fqid must start with the host node's host url, got {self.fqid}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        self.currently_adding = self._state.adding
        super().save(*args, **kwargs)
        self._propagate_post_save_to_other_nodes(created=self.currently_adding)

    def _propagate_post_save_to_other_nodes(self, created: bool) -> None:
        if not self.host_node.is_local_node:
            return
        if hasattr(self, '_deleted_propagated') and getattr(self, '_deleted_propagated'):
            print(f"Skipping propagation for deleted {self.__class__.__name__}")
            return
        from user_management.models import Node  # janky but needed for circular import prevention
        for node in Node.external_nodes.all():
            if created:
                node.send_create(self.node2node_encode_as_class_json_dict(),
                                 to=self.node2node_get_creation_url())
            else:
                node.send_update(self.node2node_encode_as_class_json_dict(),
                                 to=self.node2node_get_update_url())

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, Any]]:
        self._propagate_deletion_to_other_nodes()
        return super().delete(*args, **kwargs)

    def _propagate_deletion_to_other_nodes(self) -> None:
        if not self.host_node.is_local_node:
            return
        from user_management.models import Node
        setattr(self, '_deleted_propagated', True)
        for node in Node.external_nodes.all():
            try:
                deletion_url = self.node2node_get_deletion_url()
                node.send_delete(deletion_url)
            except Exception as e:
                print(f"Error propagating deletion to {node.name}: {e}")

    # =====================================
    # Node2node methods, these must be implemented by subclasses

    def node2node_encode_as_class_json_dict(self) -> dict[str, Any]:
        """
        Encode this object as a dictionary that can be converted to JSON, following the class's example schema
        https://uofa-cmput404.github.io/general/project.html#api-objects
        """
        raise NotImplementedError(
            f"encode_as_json must be implemented by subclasses (perhaps in `{self.__class__}`?)")

    def node2node_get_creation_url(self, author_for_inbox: Optional["Author"] = None) -> str:
        raise NotImplementedError(
            f"node2node_get_creation_url must be implemented by subclasses (perhaps in `{self.__class__}`?)")

    def node2node_get_update_url(self, author_for_inbox: Optional["Author"] = None) -> str:
        raise NotImplementedError(
            f"node2node_get_update_url must be implemented by subclasses (perhaps in `{self.__class__}`?)")

    def node2node_get_deletion_url(self, author_for_inbox: Optional["Author"] = None) -> str:
        raise NotImplementedError(
            f"node2node_get_deletion_url must be implemented by subclasses (perhaps in `{self.__class__}`?)")
    # =====================================


class AuthoredApiObject(ApiObject):
    """An API object with an author attribute
    This class does not define the author attribute, it is up to subclasses to define it (because of reverse relation naming)
    """
    class Meta:
        abstract = True

    if TYPE_CHECKING:
        author: models.ForeignKey["Author", "Author"]
