from urllib.parse import urlsplit, urlunsplit
from django import template

register = template.Library()


@register.simple_tag
def external_url_http(url: str) -> str:
    parts = urlsplit(url)
    root = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    if not root.endswith("/"):
        root += "/"
    return root
