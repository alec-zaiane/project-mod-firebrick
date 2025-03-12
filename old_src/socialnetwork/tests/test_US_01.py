from django.test import tag
from django.urls import reverse

from rest_framework import status

from socialnetwork.models import PostTextBased

from .utils_for_tests import GeneralUserStoryApiTest


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
        self.assertTrue(PostTextBased.objects.filter(
            uuid=self.sample_posts[0][0].uuid).exists())
        self.assertFalse(PostTextBased.objects.filter(
            uuid=self.sample_posts[0][0].uuid).get().is_deleted)

        # delete the post
        url = reverse("socialnetwork:api_post_delete",
                      args=[self.sample_posts[0][0].uuid])
        self.client.force_authenticate(user=self.sample_authors[0].user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that the post was deleted
        self.assertTrue(PostTextBased.objects.filter(
            uuid=self.sample_posts[0][0].uuid).get().is_deleted)

    @tag("check-medium", "security")
    def test_other_user_cannot_delete_post(self) -> None:
        """Test that an author cannot delete posts of another author"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        url = reverse("socialnetwork:api_post_delete",
                      args=[self.sample_posts[0][0].uuid])
        self.client.force_authenticate(user=self.sample_authors[1].user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        # check that the post was not deleted
        self.assertFalse(PostTextBased.objects.filter(
            uuid=self.sample_posts[0][0].uuid).get().is_deleted)
