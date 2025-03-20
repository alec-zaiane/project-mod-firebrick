from unittest import TestCase

from django.core.exceptions import ValidationError

from core.utils.validators import validate_url_returns_image


class TestValidators(TestCase):
    def test_validate_url_returns_image(self) -> None:
        # example.com should not be an image
        with self.assertRaises(ValidationError):
            validate_url_returns_image("https://example.com")

        # invalid URLs should raise an error
        with self.assertRaises(ValidationError):
            validate_url_returns_image("invalid-url")
        # imgur links should be images
        validate_url_returns_image("https://i.imgur.com/k7XVwpB.jpeg")

        # picsum links should be images
        validate_url_returns_image(
            "https://fastly.picsum.photos/id/767/200/200.jpg?hmac=xNXS1_JsopizJIWXid2sWabvtf3urglv1JXpbh6Ahvc")
