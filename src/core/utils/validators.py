"""Validators for things, these functions all return None, or raise ValidationError."""

from django.core.exceptions import ValidationError

import requests


def validate_url_returns_image(url: str, url_verbose_name: str = "URL") -> None:
    """Check if the URL returns an image.
    Use url_verbose_name to provide a more informative error message. (eg: "Profile Image URL")"""
    try:
        response = requests.head(url, timeout=5)
    except requests.RequestException as e:
        # Doesn't come up in practice because the form catches this
        raise ValidationError(f"{url_verbose_name} '{url}' is invalid.")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise ValidationError(
            f"{url_verbose_name} '{url}' is not a valid image.")
