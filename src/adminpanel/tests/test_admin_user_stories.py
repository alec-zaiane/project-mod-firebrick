from __future__ import annotations

import itertools
import os

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.db import connection
from django.apps import apps

from rest_framework.test import APITestCase
from rest_framework import status

from socialnetwork import models as socialmodels


class NodeAdminUserStoryApiTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="admin", password="pass")
        self.user.save()
        self.author = socialmodels.LocalAuthor.objects.create(user=self.user)
        self.author.save()
        self.client.force_authenticate(user=self.user)


class TestUserStory44(NodeAdminUserStoryApiTest):
    """
    Tests for User Story 44
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/44
    """

    def test_add_author(self) -> None:
        """Test adding an author through the API"""
        sample_username = "new_author"
        self.assertFalse(
            socialmodels.LocalAuthor.objects.filter(
                user__username=sample_username).exists()
        )
        url = reverse("adminpanel:api_author_create")
        response = self.client.post(
            url, {"username": sample_username, "password": "pass"})

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)
        self.assertTrue(
            socialmodels.LocalAuthor.objects.filter(
                user__username=sample_username).exists()
        )

    def test_fail_on_add_existing_username(self) -> None:
        """Test that you cannot add another author with the same username"""
        sample_username = "double_author"
        self.assertFalse(
            socialmodels.LocalAuthor.objects.filter(
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


class TestUserStory47(TestCase):
    """
    Tests for User story 47
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/47
    Written by Mosa, moved here
    """

    def test_use_postgresql_in_production(self) -> None:
        """check if postgreSQL is being used on heroku (as the issue states)"""

        if "DATABASE_URL" in os.environ:
            self.assertEqual(connection.vendor, "postgresql",
                             "PostgreSQL is required for production.")

    def test_use_sqlite_for_testing(self) -> None:
        """check if SQLite is being used for testing in local machines (as stated in the issue)"""

        self.assertEqual(connection.vendor, "sqlite", "SQLite DB must be used")

    def test_no_forbidden_databases_used(self) -> None:
        """check if no other database is being used (they are forbidden)"""

        forbidden_dbs = ["firebase", "mongodb"]
        self.assertNotIn(connection.vendor, forbidden_dbs,
                         "Forbidden database detected!")


class TestUserStory48(TestCase):
    """
    Tests for User Story 48
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/48
    Written by Mosa, moved here
    """

    def test_no_array_or_json_fields_in_models(self) -> None:
        """check if database uses ArrayField or JSONField"""
        try:
            from django.contrib.postgres.fields import ArrayField, JSONField
            POSTGRES_AVAILABLE = True
        except ImportError:
            # skip otherwise
            POSTGRES_AVAILABLE = False
        # get all models

        models = apps.get_app_config("socialnetwork").get_models()
        models_adminpanel = apps.get_app_config("adminpanel").get_models()

        for model in itertools.chain(models, models_adminpanel):
            for field in model._meta.get_fields():
                if POSTGRES_AVAILABLE and isinstance(field, (ArrayField, JSONField)):
                    self.fail(
                        f"Model {model.__name__} has either an ArrayField or JSONField ({field.name}).")
