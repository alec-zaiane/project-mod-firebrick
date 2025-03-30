from django.test import tag
from django.urls import reverse
from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.serializers import AuthorSerializer


@tag("US-following/friends")
class TestUserStory33(GeneralUserStoryApiTest):
    """
    Tests for User Story 33
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/33
        As an author, I want to know if I have "follow requests,"
        so that I can approve them.
    """

    def test_pending_follow_requests_count(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]  # follower
        author1 = self.sample_authors[1]  # followee

        # author1 initially has 0 pending requests
        self.client.force_authenticate(user=author1.user)
        pending_count_url = reverse("user_management:node2node_follow_requests-pending-count")
        resp_count_1 = self.client.get(pending_count_url)
        self.assertEqual(resp_count_1.status_code, status.HTTP_200_OK)
        self.assertIn("count", resp_count_1.data)
        self.assertEqual(resp_count_1.data["count"], 0)

        # author0 sends a follow request to author1
        follow_json = {
            "type": "follow",
            "summary": f"{author0.display_name} wants to follow {author1.display_name}",
            "actor": AuthorSerializer(author0).data,
            "object": AuthorSerializer(author1).data,
        }

        self.client.force_authenticate(user=author0.user)
        create_url = reverse("user_management:node2node_follow_requests-list")
        create_resp = self.client.post(create_url, follow_json, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_resp.data.get("type"), "follow")

        # now author1 should see exactly 1 pending request
        self.client.force_authenticate(user=author1.user)
        resp_count_2 = self.client.get(pending_count_url)
        self.assertEqual(resp_count_2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_count_2.data["count"], 1)

        # author0 sees 0 because he is the follower and has recieved no request
        self.client.force_authenticate(user=author0.user)
        resp_count_3 = self.client.get(pending_count_url)
        self.assertEqual(resp_count_3.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_count_3.data["count"], 0)
