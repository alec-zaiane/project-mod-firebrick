import uuid

from django.urls import reverse

from rest_framework import status

from user_management.models import Author
from user_management.forms import AuthorModifyForm

from core.utils.testing_utils import GeneralUserStoryApiTest

from pytest_django.asserts import assertTemplateUsed


class ProfileViewTests(GeneralUserStoryApiTest):
    def test_get_fail_on_nonexistent_profile(self) -> None:
        """Make sure a nonexistent author returns the error page"""
        self.initialize_sample_authors(1)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None  # for mypy
        self.client.force_login(user=self.sample_authors[0].user)
        bad_uuid = uuid.uuid4()
        # Make sure the UUID is not in the database
        while Author.objects.find_by_uuid(bad_uuid) is not None:
            bad_uuid = uuid.uuid4()

        url = reverse("user_management:author_profile", args=[bad_uuid])
        response = self.client.get(url)
        self.assertIn(
            f"Author with UUID {bad_uuid} Not Found",
            response.content.decode("utf-8"),
        )

    def test_view_profile(self) -> None:
        """Test that an author can view their profile"""
        self.initialize_sample_authors(2)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None
        self.client.force_login(user=self.sample_authors[0].user)
        url = reverse(
            "user_management:author_profile",
            args=[self.sample_authors[1].uuid],
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertTemplateUsed(
            response,
            "author_profile.html",
        )

    def test_fail_on_nonexistent_edit_profile(self) -> None:
        """Make sure a nonexistent author returns the error page"""
        self.initialize_sample_authors(1)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None  # for mypy
        self.client.force_login(user=self.sample_authors[0].user)
        bad_uuid = uuid.uuid4()
        # Make sure the UUID is not in the database
        while Author.objects.find_by_uuid(bad_uuid) is not None:
            bad_uuid = uuid.uuid4()

        url = reverse("user_management:author_modify", args=[bad_uuid])
        response = self.client.get(url)
        assertTemplateUsed(
            response,
            "author_not_found.html",
        )

    def test_modify_profile_get(self) -> None:
        """Test that an author can modify their profile"""
        self.initialize_sample_authors(1)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None
        self.client.force_login(user=self.sample_authors[0].user)
        url = reverse(
            "user_management:author_modify",
            args=[self.sample_authors[0].uuid],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # make sure the form is correct
        assertTemplateUsed(
            response,
            "author_modify.html",
        )

    def test_modify_profile_get_when_unauthorized(self) -> None:
        """Make sure a user cannot modify another user's profile"""
        self.initialize_sample_authors(2)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None
        self.client.force_login(user=self.sample_authors[0].user)
        url = reverse(
            "user_management:author_modify",
            args=[self.sample_authors[1].uuid],
        )
        response = self.client.get(url, follow=True)
        # make sure it's the profile page
        assertTemplateUsed(
            response,
            "author_profile.html",
        )

    def test_post_modify_profile(self) -> None:
        """Test that an author can modify their profile"""
        self.initialize_sample_authors(1)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None
        self.client.force_login(user=self.sample_authors[0].user)
        url = reverse(
            "user_management:author_modify",
            args=[self.sample_authors[0].uuid],
        )
        form = AuthorModifyForm(instance=self.sample_authors[0])
        form_data = dict(form.initial)
        form_data["username"] = "new_username"

        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertTemplateUsed(
            response,
            "author_modify_success.html",
        )
        # make sure the author was updated
        self.sample_authors[0].refresh_from_db()
        self.assertEqual(self.sample_authors[0].username, "new_username")

    def test_cannot_modify_profile_unauthorized(self) -> None:
        """Test that an author cannot modify someone else's profile"""
        self.initialize_sample_authors(2)
        self.client.force_authenticate(user=self.sample_authors[1].user)
        assert self.sample_authors[1].user is not None
        self.client.force_login(user=self.sample_authors[1].user)
        url = reverse(
            "user_management:author_modify",
            args=[self.sample_authors[0].uuid],
        )
        form = AuthorModifyForm(instance=self.sample_authors[0])
        form_data = dict(form.initial)
        form_data["username"] = "new_username"

        response = self.client.post(url, data=form_data, follow=True)
        assertTemplateUsed(
            response,
            "author_profile.html",
        )
        # make sure the author was not updated
        self.sample_authors[0].refresh_from_db()
        self.assertNotEqual(self.sample_authors[0].username, "new_username")

    def test_cannot_modify_profile_invalid(self) -> None:
        """Test that an author gets errors when modifying their profile with invalid data"""
        self.initialize_sample_authors(1)
        self.client.force_authenticate(user=self.sample_authors[0].user)
        assert self.sample_authors[0].user is not None
        self.client.force_login(user=self.sample_authors[0].user)
        url = reverse(
            "user_management:author_modify",
            args=[self.sample_authors[0].uuid],
        )
        form = AuthorModifyForm(instance=self.sample_authors[0])
        form_data = dict(form.initial)
        form_data["username"] = ""  # empty = invalid
        # make sure the form is invalid
        form = AuthorModifyForm(data=form_data, instance=self.sample_authors[0])
        self.assertFalse(form.is_valid())

        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assertTemplateUsed(
            response,
            "author_modify.html",
        )
        # make sure the author was updated
        self.sample_authors[0].refresh_from_db()
        self.assertNotEqual(self.sample_authors[0].username, "new_username")
