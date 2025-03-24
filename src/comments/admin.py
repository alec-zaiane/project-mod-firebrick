from django.contrib import admin

# Register your models here.

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin[Comment]):
    list_display = ("uuid", "author", "post", "content", "created_at", "updated_at")
    search_fields = ("content", "author__username", "uuid")
