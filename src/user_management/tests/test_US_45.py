"""
Tests for User Story 45
https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/45
"As a node admin, I want to OPTIONALLY be able to allow users to sign
up but require my OK to finally be on my node"
"""
from django.urls import reverse

from django.test import tag

from rest_framework import status

from core.utils.testing_utils import AdminUITestCase, GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author, User

from unittest import skip


@skip("Not implemented")
@tag("US-node-management", "api")
class TestUserStory45(GeneralUserStoryApiTest):

    @tag("check-fast")
    def test_create_join_request_logged_out(self) -> None:
        """Test that a logged-out user can create a join request"""
        self.client.logout()
        url = reverse("user_management:api_joinrequest_create")
        response = self.client.post(
            url, {"username": "Mr-Logged-out", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @tag("check-medium", "security")
    def test_create_join_request_logged_in(self) -> None:
        """Test that a logged-in user cannot create a join request"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("user_management:api_joinrequest_create")
        response = self.client.post(
            url, {"username": "Mr-Logged-in", "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("check-medium", "security")
    def test_join_request_fails_on_bad_password(self) -> None:
        """Test that a join request fails if the password is too short"""
        self.client.logout()
        url = reverse("user_management:api_joinrequest_create")
        response = self.client.post(
            url, {"username": "Mr-Short-password", "password": "pass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(JoinRequest.DoesNotExist):
            JoinRequest.objects.get_join_request("Mr-Short-password")
        self.assertEqual(JoinRequest.objects.count(), 0)

    @tag("check-medium")
    def test_create_existing_join_request_fail(self) -> None:
        """Test that you cannot create a join request if another one exists for the same username"""
        self.client.logout()
        url = reverse("user_management:api_joinrequest_create")
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
        url = reverse("user_management:api_joinrequest_create")
        assert self.sample_authors[0].user is not None  # for mypy
        response = self.client.post(
            url, {"username": self.sample_authors[0].user.username, "password": "passwordlong"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@tag("US-node-management", "ui")
class UITestUserStory45(AdminUITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_as_admin()

    @tag("check-fast")
    def test_approve_join_request(self) -> None:
        """Test that an admin can approve a join request"""
        self.login_as_admin()
        self.log("Creating a join request")
        join_request = JoinRequest.objects.create_join_request(
            "Mr-approve", "passwordlong"
        )
        with self.assertRaises(User.DoesNotExist):
            User.authors.get_user(join_request.username)
        self.assertEqual(
            len(Author.objects.find_authors(join_request.username)), 0)

        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        self.adminpanel_do_action("Approve selected join requests")
        self.visit("/admin/user_management/joinrequest/")

        try:
            _ = User.authors.get_user(join_request.username)
        except User.DoesNotExist:
            self.fail("User not created")
        self.assertEqual(
            len(Author.objects.find_authors(join_request.username)), 1)
        self.end_test()

    @tag("check-medium")
    def test_deny_join_request(self) -> None:
        """Test that an admin can deny a join request"""
        join_request = JoinRequest.objects.create_join_request(
            username="Mr-Deny", password="passwordlong")

        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        self.adminpanel_do_action("Deny selected join requests")
        self.visit("/admin/user_management/joinrequest/")

        self.assertTrue(JoinRequest.objects.get_join_request("Mr-Deny").is_denied)

        with self.assertRaises(User.DoesNotExist):
            User.authors.get_user(join_request.username)
        self.end_test()

    @tag("check-medium")
    def test_undeny_join_request(self) -> None:
        """Test that an admin can undo a denied join request"""
        # create a join request and deny it
        join_request = JoinRequest.objects.create_join_request(
            "mr-undeny", "passwordlong", display_name="Mr. Undeny"
        )
        join_request.deny()
        self.assertTrue(
            JoinRequest.objects.get_join_request("mr-undeny").is_denied)

        # now try to undeny it
        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        self.adminpanel_do_action("Undeny selected join requests")
        self.visit("/admin/user_management/joinrequest/")

        self.assertFalse(
            JoinRequest.objects.get_join_request("mr-undeny").is_denied)
        self.assertFalse(User.objects.filter(
            username=join_request.username).exists())
        self.end_test()

    @tag("check-slow")
    def test_delete_denied_join_request(self) -> None:
        """Test that a denied join request can be deleted"""
        join_request = JoinRequest.objects.create_join_request(
            username="Mr-Delete", password="passwordlong", display_name="Mr. Delete")
        join_request.deny()

        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        self.adminpanel_do_action("Delete selected join requests")
        self.visit("/admin/user_management/joinrequest/")

        with self.assertRaises(JoinRequest.DoesNotExist):
            JoinRequest.objects.get_join_request("Mr-Delete")
        self.end_test()

    @skip("Not implemented")
    @tag("check-slow")
    def test__can_send_join_request(self) -> None:
        self.log_out()
        # TODO: a logged out user should be able to fill in their details and send to the API
        # then a JoinRequest should be created with the correct details
        self.fail("Not implemented")
