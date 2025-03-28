from django import template

register = template.Library()


@register.simple_tag
def external_url_http(url: str) -> str:
    return url.replace("/api", "/")
