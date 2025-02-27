from typing import Any

import uuid

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status

from socialnetwork.models import LocalAuthor
from .utils_for_tests import NodeAdminUserStoryApiTest


class TestUserStory44(NodeAdminUserStoryApiTest):
    """
    Tests for User Story 44
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/44
    "As a node admin, I want to be able to add, modify, and delete authors"
    """

    # admin adding authors
    def test_add_author(self) -> None:
        """Test adding an author through the API"""
        sample_username = "new_author"
        self.assertFalse(
            LocalAuthor.objects.filter(
                user__username=sample_username).exists()
        )
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(
            url, {"username": sample_username, "password": "pass"})

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)
        self.assertTrue(
            LocalAuthor.objects.filter(
                user__username=sample_username).exists()
        )

    def test_fail_on_add_existing_username(self) -> None:
        """Test that you cannot add another author with the same username"""
        sample_username = "double_author"
        self.assertFalse(
            LocalAuthor.objects.filter(
                user__username=sample_username).exists()
        )
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(
            url, {"username": sample_username, "password": "pass"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url, {"username": sample_username, "password": "pass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_on_no_username(self) -> None:
        """Test that you cannot add an author without a username"""
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(url, {"password": "pass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_on_no_password(self) -> None:
        """Test that you cannot add an author without a password"""
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(url, {"username": "new_author"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # admin modifying authors
    def test_modify_author(self) -> None:
        """Test modifying the sample authors for success"""

        # list of updates to be made on the sample authors
        # each update is (data, (property_name, new_value))
        # ie. send `data` to the api, check if `author.property_name` == `new_value`
        updates: list[tuple[dict[str, Any], tuple[str, str]]] = [
            ({"username": "new_username"}, ("username", "new_username")),               # noqa
            ({"first_name": "new_first_name"}, ("user.first_name", "new_first_name")),  # noqa
            ({"last_name": "new_last_name"}, ("user.last_name", "new_last_name")),      # noqa
            ({"email": "new@new.com"}, ("user.email", "new@new.com")),                  # noqa
            ({"bio": "new_bio"}, ("bio", "new_bio"))                                    # noqa
        ]

        def getattr_nested(obj: Any, attr: str) -> Any:
            for a in attr.split("."):
                obj = getattr(obj, a)
            return obj

        if len(self.sample_authors) != len(updates):
            self.fail(
                "Please update either the number of sample authors or the number of updates")

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
            author = LocalAuthor.objects.get(uuid=author.uuid)
            self.assertEqual(
                getattr_nested(author, prop_name),
                expected,
                f"Author {author.uuid} does not have {prop_name} == {expected} post-update"
            )

    def test_modify_author_fail_on_unauthorized(self) -> None:
        """Test that non-admins cannot modify authors that aren't themselves"""
        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("socialnetwork:api_author_update",
                      args=[self.sample_authors[1].uuid])
        response = self.client.patch(
            url, {"username": "new_username"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_author_fail_on_double_username(self) -> None:
        """Test if updating a user to have the same username as another fails as expected"""
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

    def test_delete_user(self) -> None:
        """Test that deleting users works"""
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

    def test_delete_user_404(self) -> None:
        """Test that failing to delete a nonexistant user doesn't delete any existing users"""
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
