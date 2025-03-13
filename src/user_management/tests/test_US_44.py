from typing import Any

import uuid

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import tag

from rest_framework import status

from user_management.models import Author, JoinRequest
from core.utils.testing_utils import AdminUITestCase


from unittest import skip


# @skip("Not implemented")
@tag("US-node-management", "ui")
class TestUserStory44(AdminUITestCase):
    # TODO refactor into a UI test!
    """
    Tests for User Story 44
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/44
    "As a node admin, I want to be able to add, modify, and delete authors"
    """

    @tag("check-slow")
    def test_add_author(self) -> None:
        """Test adding an author"""
        self.login_as_admin()
        # create a join request
        self.visit("/admin/user_management/joinrequest/add")
        self.find_element_by_name("username").send_keys("new_author")
        self.find_element_by_name("display_name").send_keys("New Author")
        self.find_element_by_name("password").send_keys("pass")
        self.find_element_by_name("_save").click()

        self.assertTrue(
            JoinRequest.objects.filter(
                username="new_author").exists()
        )
        join_request = JoinRequest.objects.get(username="new_author")

        # approve the join request
        self.visit("/admin/user_management/joinrequest/")
        # select the join request
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        # approve the join request
        self.adminpanel_set_action_to("Approve selected join requests")
        self.find_element_by_name("index").click()
        self.visit("/admin/user_management/joinrequest/")  # wait for page refresh

        self.assertFalse(
            JoinRequest.objects.filter(
                username="new_author").exists()
        )
        self.assertTrue(
            Author.objects.filter(
                _user__username="new_author").exists()
        )
        self.end_test()

    @tag("check-slow")
    def test_fail_on_add_existing_username(self) -> None:
        """Test that you cannot add another author with the same username"""
        self.login_as_admin()
        # create a join request
        self.visit("/admin/user_management/joinrequest/add")
        self.find_element_by_name("username").send_keys("new_author")
        self.find_element_by_name("display_name").send_keys("New Author")
        self.find_element_by_name("password").send_keys("pass")
        self.find_element_by_name("_save").click()
        join_request = JoinRequest.objects.get(username="new_author")
        # approve it
        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request.uuid))[0].click()
        self.adminpanel_set_action_to("Approve selected join requests")
        self.find_element_by_name("index").click()
        # add another one with the same username
        self.visit("/admin/user_management/joinrequest/add")
        self.find_element_by_name("username").send_keys("new_author")
        self.find_element_by_name("display_name").send_keys("New Author")
        self.find_element_by_name("password").send_keys("pass")
        self.find_element_by_name("_save").click()
        join_request_2 = JoinRequest.objects.get(username="new_author")
        # approve it
        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request_2.uuid))[0].click()
        self.adminpanel_set_action_to("Approve selected join requests")
        self.find_element_by_name("index").click()
        messages = self.find_elements_by_selector("ul.messagelist")
        self.assertIn("is already taken", messages[0].element.text)
        self.assertEqual(JoinRequest.objects.filter(username="new_author").count(), 1)

        self.end_test()

    @skip("Not implemented")
    @tag("check-fast")
    def test_modify_author(self) -> None:
        """Test modifying the sample authors for success"""

        # list of updates to be made on the sample authors
        # each update is (data, (property_name, new_value))
        # ie. send `data` to the api, check if `author.property_name` == `new_value`
        updates: list[tuple[dict[str, Any], tuple[str, str]]] = [
            ({"username": "new_username"}, ("username", "new_username")),               # noqa
            ({"display_name": "new_display_name"}, ("display_name", "new_display_name")),  # noqa
            ({"profile_image": "new_url"}, ("profile_image", "new_url")),                # noqa
            ({"bio": "new_bio"}, ("bio", "new_bio"))                                    # noqa
        ]
        self.initialize_sample_authors(len(updates))

        def getattr_nested(obj: Any, attr: str) -> Any:
            for a in attr.split("."):
                obj = getattr(obj, a)
            return obj

        for (data, (prop_name, expected)), author in zip(updates, self.sample_authors):
            url = reverse("socialnetwork:api_author_update",
                          args=[author.uuid])
            self.assertNotEqual(
                getattr_nested(author, prop_name),
                expected,
                f"Author {author.uuid} already has {prop_name} == {expected}"
            )
            response = self.client.patch(
                url, data, format="json")
            self.assertEqual(response.status_code,
                             status.HTTP_200_OK, response.data)
            author = Author.objects.get(uuid=author.uuid)
            self.assertEqual(
                getattr_nested(author, prop_name),
                expected,
                f"Author {author.uuid} does not have {prop_name} == {expected} post-update"
            )

    @skip("Not implemented")
    @tag("check-slow", "security")
    def test_modify_author_fail_on_unauthorized(self) -> None:
        """Test that non-admins cannot modify authors that aren't themselves"""
        self.initialize_sample_authors()
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("socialnetwork:api_author_update",
                      args=[self.sample_authors[1].uuid])
        response = self.client.patch(
            url, {"username": "new_username"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @skip("Not implemented")
    @tag("check-slow")
    def test_modify_author_fail_on_double_username(self) -> None:
        """Test if updating a user to have the same username as another fails as expected"""
        self.initialize_sample_authors()
        url = reverse("socialnetwork:api_author_update",
                      args=[self.sample_authors[0].uuid])
        new_name = self.sample_authors[1].username

        response = self.client.patch(
            url, {"username", new_name}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(
            LocalAuthor.objects.get(
                uuid=self.sample_authors[0].uuid).username,
            LocalAuthor.objects.get(
                uuid=self.sample_authors[1].uuid).username
        )

    @skip("Not implemented")
    @tag("check-fast")
    def test_delete_user(self) -> None:
        """Test that deleting users works"""
        self.initialize_sample_authors()
        for user in self.sample_authors:
            self.assertTrue(
                LocalAuthor.objects.filter(
                    uuid=user.uuid
                ).exists()
            )
            authors_user = user.username

            url = reverse("adminpanel:api_author_delete", args=[user.uuid])
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertFalse(
                LocalAuthor.objects.filter(
                    uuid=user.uuid
                ).exists()
            )
            self.assertFalse(
                User.objects.filter(username=authors_user).exists()
            )

    @skip("Not implemented")
    @tag("check-slow")
    def test_delete_user_404(self) -> None:
        """Test that failing to delete a nonexistant user doesn't delete any existing users"""
        self.initialize_sample_authors()
        all_uuids: list[uuid.UUID] = [a.uuid for a in self.sample_authors]

        bad_uuid = uuid.uuid4()
        while bad_uuid in all_uuids:
            # just in case we get incredibly unlucky
            bad_uuid = uuid.uuid4()

        url = reverse("adminpanel:api_author_delete", args=[bad_uuid])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # now make sure none of the previously existing authors were deleted accidentally
        for existing_uuid in all_uuids:
            self.assertTrue(
                LocalAuthor.objects.filter(
                    uuid=existing_uuid).exists()
            )
