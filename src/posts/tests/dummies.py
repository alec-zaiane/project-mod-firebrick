"""This file contains factory classes for creating test data"""
from posts.models import Post, VisibilityTypes, PostTypes
from user_management.models import Author, Node
from django.core.files.uploadedfile import SimpleUploadedFile


def create_dummy_post(host_node: Node, author: Author, title: str = "My Post", description: str = "Description of My Post", content: str = "Content for My Post", visibility: VisibilityTypes = VisibilityTypes.PUBLIC, post_type: PostTypes = PostTypes.PLAINTEXT) -> Post:
    return Post.objects.create_post(author=author, title=title, description=description, content=content, visibility_type=visibility, post_type=post_type)


def create_dummy_post_image(name: str = 'test.gif', image: bytes | str = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b', content_type: str = 'image/gif') -> SimpleUploadedFile:
    """Creates a dummy post image. Requires an image name, and either a path to an image, or a bytestring.
    The default bytestring is a 1 pixel gif."""
    if isinstance(image, str):
        return SimpleUploadedFile(name, open(image, 'rb').read())
    return SimpleUploadedFile(name, image, content_type)


def create_dummy_invalid_post_image(name: str = 'invalid_test.gif') -> SimpleUploadedFile:
    """Creates an invalid image file. Requires an image name."""
    return SimpleUploadedFile(name, b'invalid', content_type='image/gif')
