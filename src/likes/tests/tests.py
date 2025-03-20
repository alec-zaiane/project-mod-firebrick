from django.test import TestCase
from django.core.exceptions import ValidationError

# Create your tests here.
from user_management.tests.dummies import create_dummy_local_author

from posts.models import Post, PostTypes, VisibilityTypes

from comments.models import Comment

from likes.models import Like


class LikeUnitTests(TestCase):
    def setUp(self) -> None:
        self.author = create_dummy_local_author("test", "a@a.com")
        self.post = Post.objects.create_post(
            self.author, "Test Post",
            "Test Description", "Test Content",
            PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        self.comment = Comment.objects.create_comment(
            self.author, self.post, "Test Comment", PostTypes.PLAINTEXT)

    def test_like_comment(self) -> None:
        like = Like.objects.create_like(self.author, self.comment)
        self.assertEqual(self.author.likes.count(), 1)
        self.assertEqual(self.author.likes.first(), like)
        self.assertEqual(self.comment.likes.count(), 1)
        self.assertEqual(self.comment.likes.first(), like)

    def test_like_post(self) -> None:
        like = Like.objects.create_like(self.author, self.post)
        self.assertEqual(self.author.likes.count(), 1)
        self.assertEqual(self.author.likes.first(), like)
        self.assertEqual(self.post.likes.count(), 1)
        self.assertEqual(self.post.likes.first(), like)

    def test_cannot_like_comment_twice(self) -> None:
        Like.objects.create_like(self.author, self.comment)
        with self.assertRaises(ValidationError):
            Like.objects.create_like(self.author, self.comment)

    def test_cannot_like_post_twice(self) -> None:
        Like.objects.create_like(self.author, self.post)
        with self.assertRaises(ValidationError):
            Like.objects.create_like(self.author, self.post)
