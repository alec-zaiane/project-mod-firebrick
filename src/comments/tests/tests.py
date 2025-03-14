from django.test import TestCase

from user_management.models import Node
from comments.models import Comment
from posts.tests.dummies import create_dummy_post
from user_management.tests.dummies import create_dummy_local_author


class CommentUnitTests(TestCase):
    def setUp(self) -> None:
        self.local_node = Node.objects.get_local_node()
        self.author = create_dummy_local_author("test", "a@a.com")
        self.post = create_dummy_post(self.local_node, self.author, "Test Post")

    def test_comment_creation(self) -> None:
        comment = Comment.objects.create_comment(self.author, self.post, "Test Comment")
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first(), comment)
        self.assertEqual(self.author.comments.count(), 1)
        self.assertEqual(self.author.comments.first(), comment)
