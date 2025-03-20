from django.test import TestCase
from user_management.forms import AuthorModifyForm, JoinRequestForm, LoginForm

from user_management.tests import dummies
from user_management.models import Author, JoinRequest

"""Unit Tests for User Management forms"""


class LoginFormUnitTests(TestCase):
    def test_valid_login(self) -> None:
        """Tests that a valid login can be made."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"username": "test_user", "password": "password"})
        self.assertTrue(form.is_valid())

    def test_username_invalid(self) -> None:
        """Tests that the form is invalid if the username is incorrect."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"username": "not_user", "password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_password_invalid(self) -> None:
        """Tests that the form is invalid if the password is incorrect."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"username": "test_user", "password": "not_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_username_and_password_invalid(self) -> None:
        """Tests that the form is invalid if both the username and password are incorrect."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"username": "not_user", "password": "not_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_no_password(self) -> None:
        """Tests that the form is invalid if no password is provided."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"username": "user"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ["This field is required."]
        )

    def test_no_username(self) -> None:
        """Tests that the form is invalid if no username is provided."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        form = LoginForm(data={"password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["This field is required."]
        )


class JoinRequestFormUnitTests(TestCase):
    def test_valid_join_request(self) -> None:
        """Tests that a valid join request can be made."""
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user", "password": "password"})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(JoinRequest.objects.count(), 1)

    def test_invalid_password_join_request(self) -> None:
        """Tests that the form is invalid if no password is provided."""
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user"})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ["Please provide a password."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_invalid_username_join_request(self) -> None:
        """Tests that the form is invalid if no username is provided."""
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"password": "password"})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Please provide a username."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_no_username_or_password_join_request(self) -> None:
        """Tests that the form is invalid if no username or password is provided."""
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Please provide a username."]
        )
        self.assertEqual(
            form.errors["password"], ["Please provide a password."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_request_exists_join_request(self) -> None:
        """Tests that a join request cannot be made if the username is already in an
        existing join request."""
        # Make Request
        dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")

        self.assertEqual(JoinRequest.objects.count(), 1)
        form = JoinRequestForm(data={"username": "test_user", "password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Username 'test_user' has already requested to join."]
        )
        self.assertEqual(JoinRequest.objects.count(), 1)

    def test_user_exists_join_request(self) -> None:
        """Tests that the form is invalid if the username is already taken by an
        existing author."""
        # Make account
        dummies.create_dummy_local_author(
            "test_user", "abc@a.com", password="password")

        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user", "password": "different_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Username 'test_user' is already taken."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)


class AuthorModifyFormTests(TestCase):
    def test_unchanged_form(self) -> None:
        """Tests that the form is valid when no changes are made.
        This also implicitly tests that a form is valid if bio and profile image are
        not provided."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "test_user"}, instance=author)
        self.assertTrue(form.is_valid())

    def test_valid_username_change(self) -> None:
        """Tests that the username can be changed to a valid string."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "new_user",
                                "display_name": "test_user"}, instance=author)
        self.assertTrue(form.is_valid())

    def test_valid_displayname_change(self) -> None:
        """Tests that the display name can be changed to a valid string."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "new_user"}, instance=author)
        self.assertTrue(form.is_valid())

    def test_valid_profile_image_change(self) -> None:
        """Tests that the profile image can be changed to a valid URL."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        # Image used is from https://developers.google.com/speed/webp/gallery2
        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "test_user",
                                      "profile_image": "https://www.gstatic.com/webp/gallery3/1.png"}, instance=author)
        self.assertTrue(form.is_valid())

    def test_valid_bio_change(self) -> None:
        """Tests that the bio can be changed to a valid string."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "test_user",
                                      "bio": "This is a test bio."}, instance=author)
        self.assertTrue(form.is_valid())

    def test_empty_username_change(self) -> None:
        """Tests that the username cannot be empty."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "",
                                "display_name": "test_user"}, instance=author)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Please provide a username."]
        )

    def test_empty_displayname_change(self) -> None:
        """Tests that the display name cannot be empty."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": ""}, instance=author)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["display_name"], ["Please provide a display name."]
        )

    def test_empty_username_and_displayname_change(self) -> None:
        """Tests that the username and display name cannot both be empty."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "",
                                "display_name": ""}, instance=author)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Please provide a username."]
        )
        self.assertEqual(
            form.errors["display_name"], ["Please provide a display name."]
        )

    def test_invalid_profile_image_change(self) -> None:
        """Tests that the profile image must be a valid URL."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "test_user",
                                      "profile_image": "not_a_url"}, instance=author)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["profile_image"], ["Please provide a valid Profile Image URL."]
        )

    def test_invalid_profile_image_change_but_valid_url(self) -> None:
        """Tests that the profile image must be both a valid URL and a valid image."""
        # Make account
        author = dummies.create_dummy_local_author(
            "test_user", "abc@a.com")

        form = AuthorModifyForm(data={"username": "test_user",
                                "display_name": "test_user",
                                      "profile_image": "https://www.google.com"}, instance=author)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [
                "Profile Image URL 'https://www.google.com' is not a valid image."]
        )
