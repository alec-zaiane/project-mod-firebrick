from django.test import TestCase
from user_management.forms import JoinRequestForm, LoginForm

from user_management.tests import dummies
from user_management.models import Author, JoinRequest

"""Unit Tests for User Management forms"""


class LoginFormUnitTests(TestCase):
    def test_valid_login(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"username": "test_user", "password": "password"})
        self.assertTrue(form.is_valid())

    def test_username_invalid(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"username": "not_user", "password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_password_invalid(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"username": "test_user", "password": "not_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_username_and_password_invalid(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"username": "not_user", "password": "not_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"], [
                "Please enter a correct username and password. Note that both fields may be case-sensitive."]
        )

    def test_no_password(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"username": "user"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ["This field is required."]
        )

    def test_no_username(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        form = LoginForm(data={"password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["This field is required."]
        )


class JoinRequestFormUnitTests(TestCase):
    def test_valid_join_request(self) -> None:
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user", "password": "password"})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(JoinRequest.objects.count(), 1)

    def test_invalid_password_join_request(self) -> None:
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user"})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ["Please provide a password."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_invalid_username_join_request(self) -> None:
        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"password": "password"})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Please provide a username."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_no_username_or_password_join_request(self) -> None:
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
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        join_request.approve()

        self.assertEqual(JoinRequest.objects.count(), 0)
        form = JoinRequestForm(data={"username": "test_user", "password": "different_password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["Username 'test_user' is already taken."]
        )
        self.assertEqual(JoinRequest.objects.count(), 0)
