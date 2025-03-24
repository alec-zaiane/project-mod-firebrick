from django import template

from user_management.models import Author
from posts.models import Post

register = template.Library()


@register.simple_tag
def get_follow_requests_count(author: Author) -> str:
    count = author.follow_requests_received.count()
    if count == 0:
        return ""
    return str(count)
