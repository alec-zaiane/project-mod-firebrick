"""Validators for things, these functions all return None, or raise ValidationError."""

from django.core.exceptions import ValidationError

import requests


def validate_url_returns_image(url: str, url_verbose_name: str = "URL") -> None:
    """Check if the URL returns an image.
    Use url_verbose_name to provide a more informative error message. (eg: "Profile Image URL")"""
    # from https://www.whatismybrowser.com/guides/the-latest-user-agent/firefox
    firefox_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
    try:
        response = requests.head(url, timeout=5, headers={
            "User-Agent": firefox_user_agent, "accept": "image/*"})
    except requests.RequestException as e:
        # Doesn't come up in practice because the form catches this
        raise ValidationError(f"{url_verbose_name} '{url}' is invalid.")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise ValidationError(
            f"{url_verbose_name} '{url}' is not a valid image.")
