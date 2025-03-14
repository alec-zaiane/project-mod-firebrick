"""This file contains factory classes for creating test data"""
from posts.models import Post, VisibilityTypes, PostTypes
from user_management.models import Author, Node


def create_dummy_post(host_node: Node, author: Author, title: str = "My Post", decription: str = "Description of My Post", content: str = "Content for My Post", visibility: VisibilityTypes = VisibilityTypes.PUBLIC, post_type: PostTypes = PostTypes.PLAINTEXT) -> Post:
    return Post.objects.create_post(author=author, title=title, description=decription, content=content, visibility_type=visibility, post_type=post_type)
