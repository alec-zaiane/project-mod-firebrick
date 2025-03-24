import os

from django.db import connection
from django.test import TestCase, tag


@tag("US-node-management", "check-slow")
class TestUserStory47(TestCase):
    """
    Tests for User story 47
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/47
    "As a node admin, I want everything to be stored in a well-indexed
    relational database"
    Written by Mosa, moved here
    """

    def test_use_postgresql_in_production(self) -> None:
        """check if postgreSQL is being used on heroku (as the issue states)"""

        if "DJANGO_SECRET_KEY" in os.environ:
            self.assertEqual(connection.vendor, "postgresql",
                             "PostgreSQL is required for production.")

    def test_use_sqlite_for_testing(self) -> None:
        """check if SQLite is being used for testing in local machines (as stated in the issue)"""
        if "DJANGO_SECRET_KEY" not in os.environ:
            self.assertEqual(connection.vendor, "sqlite", "SQLite DB must be used")

    def test_no_forbidden_databases_used(self) -> None:
        """check if no other database is being used (they are forbidden)"""

        forbidden_dbs = ["firebase", "mongodb"]
        self.assertNotIn(connection.vendor, forbidden_dbs,
                         "Forbidden database detected!")
