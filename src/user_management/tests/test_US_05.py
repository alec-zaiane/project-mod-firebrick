from django.test import tag

from user_management.models import Author
from core.utils.testing_utils import GeneralUserStoryApiTest


class TestUserStory05(GeneralUserStoryApiTest):
    """
    Tests for User Story 05
    As a node admin, I want to host multiple authors on my node, so I can have a friendly online community.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/5
    """

    @tag("check-medium")
    def test_host_multiple_authors(self) -> None:
        """Test hosting multiple authors"""
        self.initialize_sample_authors(5)

        fetched_authors = Author.objects.all()
        self.assertEqual(len(fetched_authors), 6)  # 5 + the auto-created self.author
