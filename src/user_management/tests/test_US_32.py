from django.test import tag
from django.urls import reverse
from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.models import FollowRequest
from user_management.serializers import AuthorSerializer


@tag("US-following/friends")
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

        follow_json = {
            "type": "follow",
            "summary": f"{author0.display_name} wants to follow {author1.display_name}",
            "actor": AuthorSerializer(author0).data,
            "object": AuthorSerializer(author1).data,
        }

        # author0 tries to follow author1
        self.client.force_authenticate(user=author0.user)
        url = reverse("user_management:node2node_follow_requests-list")
        response = self.client.post(url, follow_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # author1 can see the follow request
        self.client.force_authenticate(user=author1.user)
        fr = FollowRequest.objects.get_follow_request(author0, author1)

        # deny it
        deny_url = reverse("user_management:node2node_follow_requests-deny",
                           kwargs={"fqid": fr.get_encoded_fqid()})
        deny_response = self.client.post(deny_url)
        self.assertEqual(deny_response.status_code, status.HTTP_200_OK)

        # verify that the follow request no longer exists
        with self.assertRaises(FollowRequest.DoesNotExist):
            FollowRequest.objects.get_follow_request(author0, author1)

    def test_approve_follow_request(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]
        author1 = self.sample_authors[1]

        follow_json = {
            "type": "follow",
            "summary": f"{author0.display_name} wants to follow {author1.display_name}",
            "actor": AuthorSerializer(author0).data,
            "object": AuthorSerializer(author1).data,
        }

        # author0 tries to follow author1
        self.client.force_authenticate(user=author0.user)
        url = reverse("user_management:node2node_follow_requests-list")
        response = self.client.post(url, follow_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # author1 can see the follow request
        self.client.force_authenticate(user=author1.user)
        fr2 = FollowRequest.objects.get_follow_request(author0, author1)

        # approve it
        approve_url = reverse("user_management:node2node_follow_requests-approve",
                              kwargs={"fqid": fr2.get_encoded_fqid()})
        approve_response = self.client.post(approve_url)
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)

        # confirm author0 is in author1's followers
        self.assertTrue(author1.followers.filter(uuid=author0.uuid).exists())
        # confirm that author0 is now following author1
        self.assertTrue(author0.following.filter(uuid=author1.uuid).exists())

        # verify that the follow request no longer exists
        with self.assertRaises(FollowRequest.DoesNotExist):
            FollowRequest.objects.get_follow_request(author0, author1)
