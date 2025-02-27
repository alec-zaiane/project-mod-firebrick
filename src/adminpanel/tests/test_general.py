from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from adminpanel.models import AuthorJoinRequest
from socialnetwork.models import LocalAuthor


class AdminPanelAPITest(APITestCase):
    def setUp(self) -> None:
        """set up the users and the superusers (admin) including the join request"""

        # normal user
        self.user = User.objects.create_user(username="user", password="pass")

        # superuser (admin)
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_superuser=True)

        # authenticate as an admin
        self.client.force_authenticate(user=self.admin)

        LocalAuthor.objects.filter(user=self.admin).delete()

        # join request
        self.join_request = AuthorJoinRequest.objects.create(
            username="new", password="pass")

    def test_create_author_for_superuser(self) -> None:
        """test creating an author for a superuser"""

        url = reverse("adminpanel:api_author_create_for_superuser")
        data = {"user_id": str(self.admin.pk)}

        response = self.client.post(url, data, format="json")

        # check if the codes are correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if the author was created
        self.assertTrue(LocalAuthor.objects.filter(user=self.admin).exists())

    def test_delete_denied_join_request(self) -> None:
        """test deleting a denied join request"""

        join_request = AuthorJoinRequest.objects.create(
            username="denied", password="pass")

        # deny request before deleting it
        join_request.deny()

        url = reverse("adminpanel:api_join_request_delete",
                      args=[join_request.id])

        response = self.client.post(url)

        # check the redirect
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if the request was created
        self.assertFalse(AuthorJoinRequest.objects.filter(
            id=join_request.id).exists())
