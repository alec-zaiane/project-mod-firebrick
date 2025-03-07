from django.test import TestCase
from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, PostTextBased
from django.utils import timezone
from datetime import timedelta


class TestUserStory17(TestCase):
    """
    Test for User Story 17:
    "As an author, I want a 'stream' which shows all the posts I should know about,
     so that I don't have to switch between different pages."
    """

    def setUp(self) -> None:

        #create two users, and local authors
        self.user_a = User.objects.create_user(
            username="author_a", password="pass")
        self.author_a = LocalAuthor.objects.create(
            user=self.user_a, display_name="Author A"
        )

        self.user_b = User.objects.create_user(
            username="author_b", password="pass")
        self.author_b = LocalAuthor.objects.create(
            user=self.user_b, display_name="Author B"
        )

        #create public post (authorA)
        self.post_a = PostTextBased.objects.create(
            base_author=self.author_a,
            content="Public post by Author A",
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC,
            post_type=PostTextBased.TextPostTypes.PLAINTEXT
        )

        #create public post (authorB)
        self.post_b = PostTextBased.objects.create(
            base_author=self.author_b,
            content="Public post by Author B",
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC,
            post_type=PostTextBased.TextPostTypes.PLAINTEXT
        )

        #create a post then soft-delete so it wont show up in stream
        self.post_deleted = PostTextBased.objects.create(
            base_author=self.author_b,
            content="This post is deleted",
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC,
            post_type=PostTextBased.TextPostTypes.PLAINTEXT
        )
        self.post_deleted.delete()

    def test_stream_includes_public_posts(self) -> None:
        """
        Test that the stream for an author includes all public posts (from any author)
        and does not include deleted posts.
        """
        stream = self.author_a.get_stream()
        #The stream should include post_a (author_a’s own public post) and post_b (author_b’s public post),
        #but not the deleted post.
        self.assertIn(self.post_a, stream)
        self.assertIn(self.post_b, stream)
        self.assertNotIn(self.post_deleted, stream)

    def test_stream_sorting_order(self) -> None:
        """
        Test that the stream is sorted with the most recent posts first.
        """
        # Manipulate creation timestamps:
        self.post_a.date_created = timezone.now() - timedelta(hours=1)
        self.post_a.save()
        self.post_b.date_created = timezone.now()
        self.post_b.save()

        stream = self.author_a.get_stream()
        # Since post_b is more recent, it should appear before post_a in the sorted stream.
        self.assertEqual(stream[0], self.post_b)
