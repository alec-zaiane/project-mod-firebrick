from django.test import tag
from django.urls import reverse
from rest_framework import status
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-Following/Friends")
class TestUserStory31(GeneralUserStoryApiTest):
    """
    Tests for User Story 31
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/31
        As an author, I want to follow local authors, so that I can see their public posts.
    """

    def test_send_follow_request(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]  # follower
        author1 = self.sample_authors[1]  # target followee

        # author0 sends a follow request to author1 via the API endpoint
        self.client.force_authenticate(user=author0.user)
        url = reverse("user_management:follow_request_create")
        response = self.client.post(url, {"followee_id": str(author1.uuid)})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data.get("type"), "follow")
        self.assertIn("actor", response.data)
        self.assertIn("object", response.data)
        # check that the actor is the follower and the object is the followee
        self.assertEqual(response.data["actor"]["id"], author0.fqid)
        self.assertEqual(response.data["object"]["id"], author1.fqid)
