import itertools

from django.apps import apps
from django.test import TestCase, tag

from django.db.models import Model


@tag("US-node-management", "check-slow")
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
        all_models: list[type[Model]] = []
        for _, app_models in apps.all_models.items():
            for __, model in app_models.items():
                all_models.append(model)

        for model in itertools.chain(all_models):
            for field in model._meta.get_fields():
                if POSTGRES_AVAILABLE and isinstance(field, (ArrayField, JSONField)):
                    self.fail(
                        f"Model {model.__name__} has either an ArrayField or JSONField ({field.name}).")
