from django.test import TestCase
from user_management.forms import LoginForm

from user_management.tests import dummies
from user_management.models import Author, JoinRequest

"""Unit Tests for User Management forms"""


class UserManagementFormsUnitTests(TestCase):
    def test_valid_login(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        author = join_request.approve()

        form = LoginForm(data={"username": "test_user", "password": "password"})
        self.assertTrue(form.is_valid())

    def test_username_invalid(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        author = join_request.approve()

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
        author = join_request.approve()

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
        author = join_request.approve()

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
        author = join_request.approve()

        form = LoginForm(data={"username": "user"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"], ["This field is required."]
        )

    def test_no_username(self) -> None:
        # Make account
        join_request = dummies.create_dummy_join_request(
            "test_user", "abc@a.com", password="password")
        author = join_request.approve()

        form = LoginForm(data={"password": "password"})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["username"], ["This field is required."]
        )
