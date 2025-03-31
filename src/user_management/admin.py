from typing import Any

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from core.utils.adminpanel import admin_action_on_queryset
from user_management.forms import NodeAdminForm

from . import models
# Register your models here.


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin[models.User]):
    list_display = ('username', 'email', 'type')
    list_filter = ('type',)


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin[models.Author]):
    list_display = ('display_name', 'host_node', 'is_local_author', 'uuid')
    list_filter = ('host_node',)

    @admin.display(boolean=True, description="Is a local author")
    def is_local_author(self, obj: models.Author) -> bool:
        return obj.is_local

    @admin.action(description="Delete selected authors")
    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[models.Author]) -> None:
        for author in queryset:
            author.delete()


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin[models.Node]):
    list_display = ('name', 'host_url', 'is_local_node')
    form = NodeAdminForm
    actions = ('synchronize',)
    fieldsets = (
        (None, {
            'fields': ('name', 'host_url', 'host_site_url')
        }), ("Remote Node User", {
            "fields": ('internal_username', 'internal_password'),
            "description": "These are the credentials used to authenticate with the remote node. These should be identical to the ones stored on the remote node."
        }), ("Local User", {
            "fields": ('external_username', 'external_password'),
            "description": "These are the credentials the remote node would use to authenticate with the local node. The remote node should authenticate identically with these credentials when attempting connection."
        }), ("Properties", {
            'fields': ('is_local_node', 'is_disabled')
        })
    )

    @admin.action(description="Synchronize selected nodes")
    def synchronize(self, request: HttpRequest, queryset: QuerySet[models.Node]) -> None:
        """
        Synchronize the selected nodes with the remote nodes.
        """
        success = 0
        for node in queryset:
            try:
                node.synchronize_all()
                success += 1
            except Exception as e:
                messages.error(
                    request, f"Failed to synchronize {node.name}: {e}")
        messages.success(request, f"Successfully synchronized {success} nodes.")


@admin.register(models.JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin[models.JoinRequest]):
    list_display = ('username', 'display_name', 'is_denied')
    list_filter = ('is_denied',)
    actions = ('approve', 'deny', 'undeny', 'delete')

    @admin.action(description="Approve selected join requests")
    def approve(self, request: HttpRequest, queryset: QuerySet[models.JoinRequest]) -> None:
        admin_action_on_queryset(
            self, request, queryset,
            lambda join_request: join_request.approve(),
            success_prefix="Approved",
            failure_prefix="Failed to Approve",
            message_suffix="JoinRequests",
            stringifier=lambda join_request: join_request.username
        )

    @admin.action(description="Deny selected join requests")
    def deny(self, request: HttpRequest, queryset: QuerySet[models.JoinRequest]) -> None:
        admin_action_on_queryset(
            self, request, queryset,
            lambda join_request: join_request.deny(),
            success_prefix="Denied",
            failure_prefix="Failed to Deny",
            failure_level=messages.WARNING,
            message_suffix="JoinRequests",
            stringifier=lambda join_request: join_request.username
        )

    @admin.action(description="Undeny selected join requests")
    def undeny(self, request: HttpRequest, queryset: QuerySet[models.JoinRequest]) -> None:
        admin_action_on_queryset(
            self, request, queryset,
            lambda join_request: join_request.undeny(),
            success_prefix="Undenied",
            failure_prefix="Failed to Undeny",
            failure_level=messages.WARNING,
            message_suffix="JoinRequests",
            stringifier=lambda join_request: join_request.username
        )

    @admin.action(description="Delete selected join requests")
    def delete(self, request: HttpRequest, queryset: QuerySet[models.JoinRequest]) -> None:
        # this is slower than bulk delete, but lets each instance handle its own cleanup and verification
        admin_action_on_queryset(
            self, request, queryset,
            lambda join_request: join_request.delete(),
            success_prefix="Deleted",
            failure_prefix="Failed to Delete",
            message_suffix="JoinRequests",
            stringifier=lambda join_request: join_request.username
        )

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#conditionally-enabling-or-disabling-actions
    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
