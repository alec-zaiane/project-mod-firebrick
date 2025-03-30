from urllib.parse import urlsplit
from django import template

register = template.Library()


@register.simple_tag
def external_url(url: str) -> str:
    parts = urlsplit(url)
    return parts.netloc
