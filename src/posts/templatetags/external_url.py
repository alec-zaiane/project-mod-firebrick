from django import template

register = template.Library()


@register.simple_tag
def external_url(url: str) -> str:
    return url.replace("http://", "").replace("https://", "").replace("/api", "")
