from django.test import tag
from django.urls import reverse
from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.models import FollowRequest
from user_management.serializers import FollowRequestSerializer

from unittest import skip


@skip("Needs to be fixed")
@tag("US-Following/Friends")
class TestUserStory32(GeneralUserStoryApiTest):
    """
    Tests for User Story 32
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/32
        As an author, I want to be able to approve or deny other
        authors following me, so that I don't get followed by people I don't like.
    """

    def test_deny_follow_request(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]
        author1 = self.sample_authors[1]

        # author0 tries to follow author1
        self.client.force_authenticate(user=author0.user)
        send_url = reverse("user_management:node2node_inbox", args=[str(author1.uuid)])
        resp = self.client.post(send_url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # author1 can see the follow request
        self.client.force_authenticate(user=author1.user)
        fr = FollowRequest.objects.get_follow_request(author0, author1)

        # deny it
        deny_url = reverse("user_management:node2node_followrequest_deny", args=[str(fr.uuid)])
        deny_resp = self.client.post(deny_url)
        self.assertEqual(deny_resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(FollowRequest.objects.get_follow_request(author0, author1))

    def test_approve_follow_request(self) -> None:
        self.initialize_sample_authors(2)
        author0, author1 = self.sample_authors[:2]

        self.client.force_authenticate(user=author0.user)
        send_url = reverse("user_management:node2node_inbox", args=[str(author1.uuid)])
        self.client.post(send_url)  # send again
        fr2 = FollowRequest.objects.get_follow_request(author0, author1)

        self.client.force_authenticate(user=author1.user)
        approve_url = reverse(
            "user_management:node2node_followrequest_approve", args=[str(fr2.uuid)])
        approve_resp = self.client.post(approve_url)
        self.assertEqual(approve_resp.status_code, status.HTTP_200_OK)

        # confirm author0 is in author1's followers
        self.assertTrue(author1.followers.filter(uuid=author0.uuid).exists())
