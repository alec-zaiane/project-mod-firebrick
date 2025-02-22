"""
our socialnetwork does not use any arrays for the database, but rather relationships between models for faster access and better performance
"""

from django.test import TestCase
from django.apps import apps
from django.contrib.postgres.fields import ArrayField, JSONField

class DatabaseSchemaTest(TestCase):
    def test_no_array_or_json_fields_in_models(self):
        """
        no databse uses ArrayField or JSONField
        """
        models = apps.get_app_config("socialnetwork").get_models()  #this gets all the models in the app "socialnetwork"

        for model in models:
            for field in model._meta.get_fields():
                if isinstance(field, (ArrayField, JSONField)):
                    self.fail(f"Model {model.__name__} has either array or Json field ({field.name}).")