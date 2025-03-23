from django.test import tag
from django.urls import reverse




from core.utils.testing_utils import UITestCase

from selenium.webdriver.common.alert import Alert

from posts.models import Post




@tag("check-slow", "US-posting")
class TestUserStory10UI(UITestCase):
    """
    UI Tests for User Story 10
    As an author, I want to make posts, so I can share my thoughts and pictures with other local authors.
    """

    def test_ui_can_get_to_create_post(self) -> None:
        """Check that the user can get to the post creation via UI"""
        self.initialize_sample_authors(1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("posts:stream"))
        self.find_element_by_id("add-post-floating-button").click()
        self.assert_path(reverse("posts:create_post"))
        self.end_test()

    def test_ui_can_get_to_create_post_from_author_profile(self) -> None:
        """Check that the user can get to the post creation via their profile"""
        self.initialize_sample_authors(1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("user_management:author_profile", args=[self.sample_authors[0].uuid]))
        self.find_element_by_id("profile-create-post").find_element_by_selector("a").click()
        self.assert_path(reverse("posts:create_post"))
        self.end_test()

    def test_ui_can_create_post(self) -> None:
        self.initialize_sample_authors(1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("posts:create_post"))
        self.find_element_by_id("id_title").send_keys("Test Post")
        self.find_element_by_id("id_description").send_keys("Test Description")
        self.find_element_by_id("id_content").send_keys("Test Content")
        self.find_element_by_id("create-post-submit").click()
        self.assertEqual(Post.visible_posts.count(), 1)
        post = Post.visible_posts.first()
        assert post is not None  # for mypy
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.description, "Test Description")
        self.assertEqual(post.content, "Test Content")
        self.assertEqual(post.author, self.sample_authors[0])
        self.end_test()

    def test_can_delete_post_ui(self) -> None:
        """Check that the user can delete a post through the UI"""
        self.skip_if_on_github_actions()
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("posts:stream"))
        post = self.sample_posts[0][0]
        self.find_element_by_id(f"settings-dropdown-{post.uuid}").click()
        self.wait_for_element_by_id(f"delete-button-{post.uuid}").click()
        # created by copilot: confirm the deletion with an alert
        alert = Alert(self.driver)
        alert.accept()
        self.visit(reverse("posts:stream"))
        post.refresh_from_db()
        self.assertTrue(post.is_soft_deleted)
        self.end_test()
