from .utils_for_tests import GeneralUserStoryApiTest, JsonGenerator
from socialnetwork import models as socialmodels
from project_firebrick.settings import THIS_NODE_URL
from django.urls import reverse


class TestPostShareableLink(GeneralUserStoryApiTest):
    """
    Tests to check if posts generate shareable links correctly.
    """

    def setUp(self) -> None:
        """Set up test authors and posts."""
        super().setUp()

        self.initialize_sample_authors(num_authors=1)
        self.author = self.sample_authors[0]

        #create posts with different visibility
        self.public_post = socialmodels.PostTextBased.objects.create(
            base_author=self.author,
            content="Public post content",
            visibility_type=socialmodels.Post.VisibilityTypes.PUBLIC,
            post_type=socialmodels.PostTextBased.TextPostTypes.PLAINTEXT,
        )

        self.unlisted_post = socialmodels.PostTextBased.objects.create(
            base_author=self.author,
            content="Unlisted post content",
            visibility_type=socialmodels.Post.VisibilityTypes.UNLISTED,
            post_type=socialmodels.PostTextBased.TextPostTypes.PLAINTEXT,
        )

        self.friends_only_post = socialmodels.PostTextBased.objects.create(
            base_author=self.author,
            content="Friends-only post content",
            visibility_type=socialmodels.Post.VisibilityTypes.FRIENDS_ONLY,
            post_type=socialmodels.PostTextBased.TextPostTypes.PLAINTEXT,
        )

    def test_public_post_has_valid_shareable_link(self)-> None:
        """Test that a public post has a valid frontend URL."""

        expected_url = f"{THIS_NODE_URL}{reverse('socialnetwork:view_post', args=[self.public_post.uuid])}"
        self.assertEqual(self.public_post.get_absolute_url(), expected_url)

    def test_unlisted_post_has_valid_shareable_link(self) -> None:
        """Test that an unlisted post has a valid frontend URL."""

        expected_url = f"{THIS_NODE_URL}{reverse('socialnetwork:view_post', args=[self.unlisted_post.uuid])}"
        self.assertEqual(self.unlisted_post.get_absolute_url(), expected_url)

    def test_friends_only_post_has_no_shareable_link(self) -> None:

        """Test that a friends-only post does not return a shareable link."""
        with self.assertRaises(ValueError):
            self.friends_only_post.get_absolute_url()
