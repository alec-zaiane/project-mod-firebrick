from django.test import tag
from django.urls import reverse
from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-Following/Friends")
class TestUserStory34(GeneralUserStoryApiTest):
    """
    Tests for User Story 34
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/34
        As an author, I want to unfollow authors I am following,
        so that I don't have to see their posts anymore.
    """

    def test_unfollow_author(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]  # follower
        author1 = self.sample_authors[1]  # followee

        # manually simulate a follow relationship
        author0.following.add(author1)

        # confirm the follow relationship exists
        self.assertTrue(author0.following.filter(uuid=author1.uuid).exists())
        self.assertTrue(author1.followers.filter(uuid=author0.uuid).exists())

        # author0 logs in and unfollows author1
        self.client.force_authenticate(user=author0.user)
        unfollow_url = reverse("user_management:node2node_authors-unfollow",
                               kwargs={"fqid": author1.get_encoded_fqid()})
        response = self.client.post(unfollow_url)

        # check for success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # confirm the relationship is removed
        self.assertFalse(author0.following.filter(uuid=author1.uuid).exists())
        self.assertFalse(author1.followers.filter(uuid=author0.uuid).exists())
