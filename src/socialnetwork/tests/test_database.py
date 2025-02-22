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