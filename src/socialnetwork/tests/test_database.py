"""
Our social network does not use any arrays for the database, 
but rather relationships between models for faster access and better performance.
"""

from django.test import TestCase
from django.apps import apps
from django.db import connection
import os

#try importing PostgreSQL-specific fields
try:
    from django.contrib.postgres.fields import ArrayField, JSONField
    POSTGRES_AVAILABLE = True
except ImportError:
    #skip otherwise
    POSTGRES_AVAILABLE = False  

class DatabaseSchemaTest(TestCase):

    def test_no_array_or_json_fields_in_models(self) -> None:
        """
        check if database uses ArrayField or JSONField"""
        #get all models
        models = apps.get_app_config("socialnetwork").get_models()

        for model in models:
            for field in model._meta.get_fields():
                if POSTGRES_AVAILABLE and isinstance(field, (ArrayField, JSONField)):
                    self.fail(f"Model {model.__name__} has either an ArrayField or JSONField ({field.name}).")

#check the type of databases that are being used for both local and in production
class DatabaseTypeTest(TestCase):

    def test_use_postgresql_in_production(self) -> None:
        """check if postgreSQL is being used on heroku (as the issue states)"""

        if "DATABASE_URL" in os.environ:
            self.assertEqual(connection.vendor, "postgresql", "PostgreSQL is required for production.")

    def test_use_sqlite_for_testing(self) -> None:
        """check if SQLite is being used for testing in local machines (as stated in the issue)"""

        self.assertEqual(connection.vendor, "sqlite", "SQLite DB must be used")

    def test_no_forbidden_databases_used(self) -> None:
        """check if no other database is being used (they are forbidden)"""

        forbidden_dbs = ["firebase", "mongodb"]
        self.assertNotIn(connection.vendor, forbidden_dbs, "Forbidden database detected!")