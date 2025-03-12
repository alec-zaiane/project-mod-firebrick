from django.urls import reverse

from django.contrib.auth.models import User
from django.test import tag

from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author


from unittest import skip


@skip("Not implemented")
@tag("US-node-management")
class TestUserStory45(GeneralUserStoryApiTest):
    """
    Tests for User Story 45
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/45
    "As a node admin, I want to OPTIONALLY be able to allow users to sign
    up but require my OK to finally be on my node"
    """
    # TODO refactor into a UI test!

    @tag("check-slow", "security")
    def test_fail_to_add_user(self) -> None:
        """Test that a non-admin cannot add an author"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(
            url, {"username": "new_author", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("check-fast")
    def test_create_join_request_logged_out(self) -> None:
        """Test that a logged-out user can create a join request"""
        self.client.logout()
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": "Mr-Logged-out", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @tag("check-medium", "security")
    def test_create_join_request_logged_in(self) -> None:
        """Test that a logged-in user cannot create a join request"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": "Mr-Logged-in", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("check-medium", "security")
    def test_create_join_request_superuser(self) -> None:
        """Test that a superuser can create a join request"""
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": "Mr-Superuser", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @tag("check-medium", "security")
    def test_join_request_fails_on_bad_password(self) -> None:
        """Test that a join request fails if the password is too short"""
        self.client.logout()
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": "Mr-Short-password", "password": "pass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(AuthorJoinRequest.objects.filter(
            username="Mr-Short-password").exists()
        )

    @tag("check-medium")
    def test_create_existing_join_request_fail(self) -> None:
        """Test that you cannot create a join request if another one exists for the same username"""
        self.client.logout()
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": "Mr-Double-entry", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url, {"username": "Mr-Double-entry", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("check-medium")
    def test_create_join_request_matching_username_fail(self) -> None:
        """Test that you cannot create a join request with a username that matches an existing user"""
        self.initialize_sample_authors()
        self.client.logout()
        url = reverse("adminpanel:api_join_request_create")
        response = self.client.post(
            url, {"username": self.sample_authors[0].user.username, "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("check-fast")
    def test_approve_join_request(self) -> None:
        """Test that an admin can approve a join request"""
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Approve", password="passwordlong")
        self.assertFalse(
            User.objects.filter(username=join_request.username).exists())
        self.assertFalse(
            LocalAuthor.objects.filter(user__username=join_request.username).exists())

        url = reverse("adminpanel:api_join_request_approve",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            User.objects.filter(username=join_request.username).exists())
        self.assertTrue(
            LocalAuthor.objects.filter(user__username=join_request.username).exists())

    @tag("check-slow")
    def test_approve_nonexistent_join_request_fail(self) -> None:
        """Test that an admin cannot approve a non-existent join request"""
        url = reverse("adminpanel:api_join_request_approve", args=[999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @tag("check-slow", "security")
    def test_non_admin_cannot_approve_join_request(self) -> None:
        """Test that a non-admin cannot approve a join request"""
        self.initialize_sample_authors()
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Approve", password="passwordlong")
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("adminpanel:api_join_request_approve",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(
            username=join_request.username).exists())
        self.assertFalse(LocalAuthor.objects.filter(
            user__username=join_request.username).exists())

    @tag("check-slow", "security")
    def test_logged_out_cannot_approve_join_request(self) -> None:
        """Test that a logged-out user cannot approve a join request"""
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Approve", password="passwordlong")
        self.client.logout()
        url = reverse("adminpanel:api_join_request_approve",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(User.objects.filter(
            username=join_request.username).exists())
        self.assertFalse(LocalAuthor.objects.filter(
            user__username=join_request.username).exists())

    @tag("check-medium")
    def test_deny_join_request(self) -> None:
        """Test that an admin can deny a join request"""
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Deny", password="passwordlong")

        url = reverse("adminpanel:api_join_request_deny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(AuthorJoinRequest.objects.get(
            id=join_request.pk).is_denied)

        self.assertFalse(
            User.objects.filter(username=join_request.username).exists())

    @tag("check-medium")
    def test_undeny_join_request(self) -> None:
        """Test that an admin can undo a denied join request"""
        # create a join request and deny it
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Undeny", password="passwordlong")
        join_request.deny()
        self.assertTrue(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)

        # now try to undeny it
        url = reverse("adminpanel:api_join_request_undeny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)
        self.assertFalse(User.objects.filter(
            username=join_request.username).exists())

    @tag("check-slow", "security")
    def test_user_cannot_deny_or_undeny_join_request(self) -> None:
        """Test that a non-admin cannot deny a join request"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        # create a join request and try to deny it
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Deny", password="passwordlong")
        url = reverse("adminpanel:api_join_request_deny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(AuthorJoinRequest.objects.get(
            id=join_request.pk).is_denied)

        # now try undenying
        join_request.deny()
        self.assertTrue(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)
        url = reverse("adminpanel:api_join_request_undeny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)

    @tag("check-slow", "security")
    def test_logged_out_cannot_deny_or_undeny_join_request(self) -> None:
        """Test that a logged-out user cannot deny a join request"""
        self.client.logout()
        # create a join request and try to deny it
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Deny", password="passwordlong")
        url = reverse("adminpanel:api_join_request_deny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(AuthorJoinRequest.objects.get(
            id=join_request.pk).is_denied)

        # now try undenying
        join_request.deny()
        self.assertTrue(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)
        url = reverse("adminpanel:api_join_request_undeny",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            AuthorJoinRequest.objects.get(id=join_request.pk).is_denied)

    @tag("check-slow")
    def test_cannot_delete_undenied_join_request(self) -> None:
        """Test that a non-denied join request cannot be deleted"""
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Delete", password="passwordlong")
        url = reverse("adminpanel:api_join_request_delete",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(AuthorJoinRequest.objects.filter(
            id=join_request.pk).exists())

    @tag("check-slow")
    def test_delete_denied_join_request(self) -> None:
        """Test that a denied join request can be deleted"""
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Delete", password="passwordlong")
        join_request.deny()
        url = reverse("adminpanel:api_join_request_delete",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AuthorJoinRequest.objects.filter(
            id=join_request.pk).exists())

    @tag("check-slow", "security")
    def test_user_cannot_delete_join_request(self) -> None:
        """Test that a non-admin cannot delete a join request"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Delete", password="passwordlong")
        url = reverse("adminpanel:api_join_request_delete",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AuthorJoinRequest.objects.filter(
            id=join_request.pk).exists())

    @tag("check-slow", "security")
    def test_logged_out_cannot_delete_join_request(self) -> None:
        """Test that a logged-out user cannot delete a join request"""
        self.client.logout()
        join_request = AuthorJoinRequest.objects.create(
            username="Mr-Delete", password="passwordlong")
        url = reverse("adminpanel:api_join_request_delete",
                      args=[join_request.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(AuthorJoinRequest.objects.filter(
            id=join_request.pk).exists())
