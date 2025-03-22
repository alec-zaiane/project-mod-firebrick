from django.test import tag
from django.urls import reverse

from rest_framework import status


from core.utils.testing_utils import GeneralUserStoryApiTest, UITestCase

from selenium.webdriver.common.alert import Alert

from posts.models import Post


@tag("US-posting")
class TestUserStory01(GeneralUserStoryApiTest):
    """
    Tests for User Story 01
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/1
    As an author, I want to delete my own posts locally
    """

    @tag("check-fast")
    def test_delete_post(self) -> None:
        """Test that an author can delete their own posts"""
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1)

        # check that the post was created
        self.assertEqual(self.sample_authors[0].posts.count(), 1)
        self.assertFalse(self.sample_authors[0].posts.get().is_soft_deleted)
        post_uuid = self.sample_authors[0].posts.get().uuid
        # delete the post
        url = reverse("posts:api_posts-detail",
                      args=[post_uuid])
        self.client.force_authenticate(user=self.sample_authors[0].user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check that the post was deleted
        self.assertTrue(Post.objects.get(uuid=post_uuid).is_soft_deleted)
        # make sure it no longer exists in author.posts
        self.assertEqual(self.sample_authors[0].posts.count(), 0)

    @tag("check-medium", "security")
    def test_other_user_cannot_delete_post(self) -> None:
        """Test that an author cannot delete posts of another author"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        url = reverse("posts:api_posts-detail",
                      args=[self.sample_authors[0].posts.get().uuid])
        self.client.force_authenticate(user=self.sample_authors[1].user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # check that the post was not deleted
        self.assertFalse(self.sample_authors[0].posts.get().is_soft_deleted)


@tag("check-slow", "US-posting")
class TestUserStory01UI(UITestCase):
    """
    UI Tests for User Story 01
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
