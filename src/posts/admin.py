from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from core.utils.adminpanel import admin_action_on_queryset

from . import models
# Register your models here.


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin[models.Post]):
    list_display = ("uuid", "author", "title", "description",
                    "created_at", "updated_at", "is_soft_deleted")
    search_fields = ("title", "author__username", "uuid")
    list_filter = ("created_at", "updated_at")
    actions = ("soft_delete", "restore")

    @admin.action(description="Soft delete selected posts")
    def soft_delete(self, request: HttpRequest, queryset: QuerySet[models.Post]) -> None:
        admin_action_on_queryset(
            self, request, queryset,
            lambda post: post.soft_delete(),
            success_prefix="Soft deleted",
            failure_prefix="Failed to soft delete",
            message_suffix="posts",
            stringifier=lambda post: f"{post.title} ({str(post.uuid)[:8]}) by {post.author.username}"
        )

    @admin.action(description="Restore selected posts")
    def restore(self, request: HttpRequest, queryset: QuerySet[models.Post]) -> None:
        admin_action_on_queryset(
            self, request, queryset,
            lambda post: post.restore(),
            success_prefix="Restored",
            failure_prefix="Failed to restore",
            message_suffix="posts",
            stringifier=lambda post: f"{post.title} ({str(post.uuid)[:8]}) by {post.author.username}"
        )
