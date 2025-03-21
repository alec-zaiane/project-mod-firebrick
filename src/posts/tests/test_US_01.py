from django.test import tag
from django.urls import reverse

from rest_framework import status


from core.utils.testing_utils import GeneralUserStoryApiTest, UITestCase

from selenium.webdriver.common.alert import Alert


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

        # delete the post
        url = reverse("posts:api_posts-detail",
                      args=[self.sample_authors[0].posts.get().uuid])
        self.client.force_authenticate(user=self.sample_authors[0].user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check that the post was deleted
        self.assertTrue(self.sample_authors[0].posts.get().is_soft_deleted)

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

    def test_can_delete_post_ui(self) -> None:
        """Check that the user can delete a post through the UI"""
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1)
        self.login_as(self.sample_authors[0])
        self.visit(reverse("posts:stream"))
        post = self.sample_posts[0][0]
        self.find_element_by_id(f"settings-dropdown-{post.uuid}").click()
        if self.is_in_github_actions:
            # https://stackoverflow.com/questions/72525442/python-selenium-change-the-visiblity-of-the-element-from-hidden-to-visible-then
            self.driver.execute_script(
                # type: ignore
                f"document.getElementById('settings-dropdown-content-{post.uuid}').style.visibility = 'visible';")
        self.wait_for_element_by_id(f"delete-button-{post.uuid}").click()
        # created by copilot: confirm the deletion with an alert
        if not self.is_in_github_actions:
            alert = Alert(self.driver)
            alert.accept()
        self.visit(reverse("posts:stream"))
        post.refresh_from_db()
        self.assertTrue(post.is_soft_deleted)
        self.end_test()
