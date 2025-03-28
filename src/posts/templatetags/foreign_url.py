from django import template

register = template.Library()


@register.simple_tag
def foreign_url(url: str) -> str:
    return url.replace("http://", "").replace("https://", "").replace("/api", "")
