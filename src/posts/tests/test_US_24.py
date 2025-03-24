from core.utils.testing_utils import GeneralUserStoryApiTest
from posts.models import Post, VisibilityTypes, PostTypes
from user_management.models import Node
from django.urls import reverse

from django.core.exceptions import ValidationError


class TestUserStory24(GeneralUserStoryApiTest):
    """
    Tests to check if posts generate shareable links correctly.
    """

    def setUp(self) -> None:
        """Set up test authors and posts."""
        super().setUp()

        self.initialize_sample_authors(num_authors=1)

        # Create test posts
        self.public_post = Post.objects.create_post(
            author=self.author,
            content="This is a public post",
            title="Post title",
            description="Post Description",
            visibility_type=VisibilityTypes.PUBLIC,
            post_type=PostTypes.PLAINTEXT
        )

        self.friends_only_post = Post.objects.create_post(
            author=self.author,
            content="This is a friends-only post",
            title="Post title",
            description="Post Description",
            visibility_type=VisibilityTypes.FRIENDS_ONLY,
            post_type=PostTypes.PLAINTEXT
        )

        self.unlisted_post = Post.objects.create_post(
            author=self.author,
            content="This is an unlisted post",
            title="Post title",
            description="Post Description",
            visibility_type=VisibilityTypes.UNLISTED,
            post_type=PostTypes.PLAINTEXT
        )

        self.THIS_NODE_URL = Node.objects.get_local_node().host_site_url

    def test_public_post_has_valid_shareable_link(self) -> None:
        """Test that a public post has a valid frontend URL."""

        expected_url = f"{self.THIS_NODE_URL}{reverse('posts:view_post', args=[self.public_post.uuid])}"
        self.assertEqual(self.public_post.get_absolute_url(), expected_url)

    def test_unlisted_post_has_valid_shareable_link(self) -> None:
        """Test that an unlisted post has a valid frontend URL."""

        expected_url = f"{self.THIS_NODE_URL}{reverse('posts:view_post', args=[self.unlisted_post.uuid])}"
        self.assertEqual(self.unlisted_post.get_absolute_url(), expected_url)

    def test_friends_only_post_has_no_shareable_link(self) -> None:
        """Test that a friends-only post does not return a shareable link."""
        with self.assertRaises(ValidationError):
            self.friends_only_post.get_absolute_url()
