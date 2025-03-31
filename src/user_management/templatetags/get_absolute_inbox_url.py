from django import template

from user_management.models import Author

from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_absolute_inbox_url(author: Author) -> str:
    """
    Get the absolute URL for the author's inbox.
    """
    return author.host_node._make_absolute_url(
        reverse("user_management:node2node_inbox", args=[author.get_encoded_fqid()])
    )
