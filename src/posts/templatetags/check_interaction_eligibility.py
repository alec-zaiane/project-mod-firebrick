from typing import Optional

from django import template

from user_management.models import Author
from posts.models import Post

register = template.Library()


@register.simple_tag
def check_interaction_eligibility(author: Optional[Author], target: Post) -> bool:
    if author is None:
        return False
    return Post.visible_posts.get_posts_visible_to_author(author).filter(uuid=target.uuid).exists()
