from django.test import tag
from django.urls import reverse
from posts.models import Post, PostTypes, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest, UITestCase
from user_management.models import Author


@tag("US-reading")
class TestUserStory60(GeneralUserStoryApiTest):
    """
    Tests for User Story 60
    "As an author, I want my stream page to not show me posts that have been deleted"
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/60
    """
    @tag("check-fast")
    def test_deleted_post_not_in_stream(self) -> None:
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.assertIn(self.sample_posts[1][0], self.sample_authors[0].get_stream(0, 10))
        self.sample_posts[1][0].soft_delete()
        self.assertNotIn(self.sample_posts[1][0], self.sample_authors[0].get_stream(0, 10))

    def test_deleted_post_not_in_author_posts(self) -> None:
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.assertIn(self.sample_posts[1][0], self.sample_authors[1].posts.all())
        self.sample_posts[1][0].soft_delete()
        self.assertTrue(self.sample_posts[1][0].is_soft_deleted)
        self.assertNotIn(self.sample_posts[1][0], self.sample_authors[1].posts.all())
