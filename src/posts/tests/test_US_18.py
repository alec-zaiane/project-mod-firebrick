from django.test import tag
from datetime import timedelta
from django.utils import timezone

from posts.models import Post, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-reading", "check-medium")
class TestUserStory18(GeneralUserStoryApiTest):
    """
    Tests for User Story 18
    "As an author, I want my "stream" page to be sorted with the most recent posts first."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/18
    """

    def setUp(self) -> None:
        super().setUp()
        # create test user and author
        self.initialize_sample_authors(1)
        self.followed_author = self.sample_authors[0]

        # set up following relationship
        self.author.following.add(self.followed_author)

    @tag("check-fast")
    def test_stream_shows_posts_newest_first(self) -> None:
        """
        Test that stream shows most recent posts first.
        """
        # create sample posts
        self.initialize_sample_text_posts(
            posts_per_author=3, visibility_type=VisibilityTypes.PUBLIC
        )

        posts = list(
            Post.visible_posts.filter(author=self.followed_author).order_by(
                "created_at"
            )
        )

        # set timestamps for ordering
        posts[0].created_at = timezone.now() - timedelta(days=2)
        posts[0].save()
        posts[1].created_at = timezone.now() - timedelta(days=1)
        posts[1].save()

        # get posts in stream directly
        stream_posts = list(
            Post.visible_posts.get_posts_in_stream_of_author(
                self.author,
                paginate_start=0,
                paginate_count=10,
            )
        )
        self.assertEqual(len(stream_posts), 3)

        # verify newest to oldest ordering
        self.assertEqual(stream_posts[0], posts[2], "Newest post should be first")
        self.assertEqual(stream_posts[1], posts[1], "Middle post should be second")
        self.assertEqual(stream_posts[2], posts[0], "Oldest post should be last")
