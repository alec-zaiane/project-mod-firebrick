from django.test import tag
from django.urls import reverse
from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest

from unittest import skip


@skip("Not implemented")
@tag("US-Following/Friends")
class TestUserStory33(GeneralUserStoryApiTest):
    """
    Tests for User Story 33
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/33
        As an author, I want to know if I have "follow requests,"
        so I can approve them.
    """

    def test_can_view_follow_requests(self) -> None:
        self.initialize_sample_authors(2)
        author0 = self.sample_authors[0]
        author1 = self.sample_authors[1]

        # author0 follow author1
        self.client.force_authenticate(user=author0.user)
        send_url = reverse("user_management:node2node_inbox", args=[str(author1.uuid)])
        send_resp = self.client.post(send_url)
        self.assertEqual(send_resp.status_code, status.HTTP_201_CREATED)

        # author1 can see the follow request in list_follow_requests
        self.client.force_authenticate(user=author1.user)
        list_url = reverse("user_management:TODO_FIGURE_OUT")
        list_resp = self.client.get(list_url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        # we expect exactly 1 follow request
        self.assertEqual(len(list_resp.data), 1)
        self.assertEqual(list_resp.data[0]["actor"]["uuid"], str(author0.uuid))
        self.assertEqual(list_resp.data[0]
                         ["target"]["uuid"], str(author1.uuid))
