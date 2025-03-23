from django.test import tag
from django.urls import reverse

from rest_framework import status


from core.utils.testing_utils import GeneralUserStoryApiTest

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
