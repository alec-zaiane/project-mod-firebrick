from django.contrib import admin

from likes.models import Like
# Register your models here.


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin[Like]):
    list_display = ("uuid", "author", "target", "created_at")

    @admin.display(description="Target")
    def target(self, like: Like) -> str:
        if like._target_post:
            return f"Post: {str(like._target_post)}"
        if like._target_comment:
            return f"Comment: {str(like._target_comment)}"
        return "Unknown target"
