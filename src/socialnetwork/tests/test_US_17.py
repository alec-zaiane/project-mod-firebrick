from django.test import tag
from django.urls import reverse
from rest_framework.test import APITestCase
from socialnetwork.models import PostTextBased, Post
from .utils_for_tests import GeneralUserStoryApiTest
from django.utils import timezone
from datetime import timedelta


@tag("US-Reading")
class TestUserStory17(GeneralUserStoryApiTest):
    """
    Test for User Story 17:
    "As an author, I want a 'stream' which shows all the posts I should know about,
     so that I don't have to switch between different pages."
    """

    def setUp(self) -> None:
        """
        Set up test data using the utility functions.
        """
        super().setUp()

        #2 sample authors
        self.initialize_sample_authors(2)

        #create 2 public posts (one per author)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.author_a = self.sample_authors[0]
        self.author_b = self.sample_authors[1]

        self.post_a = self.sample_posts[0][0]  # Author A's post
        self.post_b = self.sample_posts[1][0]  # Author B's post

        #soft deleted Post
        self.post_deleted = PostTextBased.objects.create(
            base_author=self.author_b,
            content="This post is deleted",
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC,
            post_type=PostTextBased.TextPostTypes.PLAINTEXT
        )
        #soft delete the post
        self.post_deleted.delete()

    @tag("check-fast")
    def test_stream_includes_public_posts(self) -> None:
        """
        Test that the stream for an author includes all public posts (from any author)
        and does not include deleted posts.
        """
        stream = self.author_a.get_stream()

        #the stream should include post_a (author_a’s own public post) and post_b (author_b’s public post), but not the deleted Post
        self.assertIn(self.post_a, stream)
        self.assertIn(self.post_b, stream)
        self.assertNotIn(self.post_deleted, stream)

    @tag("check-fast")
    def test_stream_sorting_order(self) -> None:
        """
        Test that the stream is sorted with the most recent posts first.
        """
        #calculate timestamps
        self.post_a.date_created = timezone.now() - timedelta(hours=1)
        self.post_a.save()
        self.post_b.date_created = timezone.now()
        self.post_b.save()

        stream = self.author_a.get_stream()

        #since post_b is more recent, it should appear before post_a in the sorted stream.
        self.assertEqual(stream[0], self.post_b)
