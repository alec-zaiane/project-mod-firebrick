from typing import Optional

from django import template

from likes.models import Like
from user_management.models import Author
from posts.models import Post
from comments.models import Comment

register = template.Library()


@register.simple_tag
def check_liked(author: Optional[Author], target: Post | Comment) -> bool:
    if author is None:
        return False
    return Like.objects.check_liked(author, target)
