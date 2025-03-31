from django.test import tag
from django.urls import reverse
from rest_framework import status
from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.models import FollowRequest
from user_management.serializers import AuthorSerializer


@tag("US-following/friends")
class TestUserStory35(GeneralUserStoryApiTest):
    """
    Tests for User Story 35
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/35
        As an author, if I am following another author, and they are following me (only after both
        follow requests are approved), I want us to be considered friends, so that they can see my
        friends-only posts (the 'friends' property).
    """

    def test_mutual_follow_means_friends(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]
        author1 = self.sample_authors[1]

        # control: confirm that they are not friends before following each other
        self.assertNotIn(author1, author0.friends)
        self.assertNotIn(author0, author1.friends)

        # author0 sends follow request to author1
        self.client.force_authenticate(user=author0.user)
        follow_requests_url = reverse("user_management:node2node_follow_requests-list")

        follow_json_0_to_1 = {
            "type": "follow",
            "summary": f"{author0.display_name} wants to follow {author1.display_name}",
            "actor": AuthorSerializer(author0).data,
            "object": AuthorSerializer(author1).data,
        }
        resp_0_to_1 = self.client.post(follow_requests_url, follow_json_0_to_1, format="json")
        self.assertEqual(resp_0_to_1.status_code, status.HTTP_201_CREATED)

        # author1 approves
        self.client.force_authenticate(user=author1.user)
        fr_0_to_1 = FollowRequest.objects.get_follow_request(author0, author1)
        approve_url_0_to_1 = reverse(
            "user_management:node2node_follow_requests-approve", kwargs={"uuid": fr_0_to_1.uuid})
        approve_resp_0_to_1 = self.client.post(approve_url_0_to_1)
        self.assertEqual(approve_resp_0_to_1.status_code, status.HTTP_200_OK)

        # author1 sends follow request to author0
        self.client.force_authenticate(user=author1.user)
        follow_json_1_to_0 = {
            "type": "follow",
            "summary": f"{author1.display_name} wants to follow {author0.display_name}",
            "actor": AuthorSerializer(author1).data,
            "object": AuthorSerializer(author0).data,
        }
        resp_1_to_0 = self.client.post(follow_requests_url, follow_json_1_to_0, format="json")
        self.assertEqual(resp_1_to_0.status_code, status.HTTP_201_CREATED)

        # right before author0 approves, they should still not be friends
        author0.refresh_from_db()
        author1.refresh_from_db()
        self.assertNotIn(author1, author0.friends)
        self.assertNotIn(author0, author1.friends)

        # author0 approves
        self.client.force_authenticate(user=author0.user)
        fr_1_to_0 = FollowRequest.objects.get_follow_request(author1, author0)
        approve_url_1_to_0 = reverse(
            "user_management:node2node_follow_requests-approve", kwargs={"uuid": fr_1_to_0.uuid})
        approve_resp_1_to_0 = self.client.post(approve_url_1_to_0)
        self.assertEqual(approve_resp_1_to_0.status_code, status.HTTP_200_OK)

        # confirm that they are now mutuals/friends
        author0.refresh_from_db()
        author1.refresh_from_db()

        self.assertIn(author1, author0.friends, "author1 should appear in author0.friends")
        self.assertIn(author0, author1.friends, "author0 should appear in author1.friends")
