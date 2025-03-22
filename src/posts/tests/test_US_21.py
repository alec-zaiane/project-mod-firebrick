from django.test import tag
from django.urls import reverse

from rest_framework import status

from posts.models import Post, VisibilityTypes

from core.utils.testing_utils import UITestCase


@tag("US-Visibility")
class TestUserStory21(UITestCase):
    """
    Tests for User Story 21
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/21
    As an author, I want to be able to make my posts "friends-only," so that I don't have to worry about people I don't know seeing them.
    """

    @tag("check-slow")
    def test_make_post_friends_only(self) -> None:
        """Test that an author can make a post friends-only"""
        self.initialize_sample_authors(1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("posts:create_post"))
        self.find_element_by_id("id_title").send_keys("Test Post")
        self.find_element_by_id("id_content").send_keys("Test Content")

        # use the dropdown to choose "friends only"
        self.find_element_by_id("id_visibility_type").as_selector_choose_value("Friends Only")

        # submit
        self.find_element_by_id("create-post-submit").click()
        self.assertEqual(Post.visible_posts.count(), 1)
        post = Post.visible_posts.first()
        assert post is not None  # for mypy
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "Test Content")
        self.assertEqual(post.author, self.sample_authors[0])
        self.assertEqual(post.visibility_type, VisibilityTypes.FRIENDS_ONLY)
        self.end_test()
