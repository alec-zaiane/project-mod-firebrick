import itertools

from django.test import TestCase
from django.apps import apps


class TestUserStory48(TestCase):
    """
    Tests for User Story 48
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/48
    "As a node admin, I don't want arrays to be stored in database fields"
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
