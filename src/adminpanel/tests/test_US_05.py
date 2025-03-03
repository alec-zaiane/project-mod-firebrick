from typing import Any

import uuid

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import tag

from rest_framework import status

from socialnetwork.models import LocalAuthor
from .utils_for_tests import NodeAdminUserStoryApiTest


class TestUserStory05(NodeAdminUserStoryApiTest):
    """
    Tests for User Story 05
    As a node admin, I want to host multiple authors on my node, so I can have a friendly online community.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/5
    """

    @tag("check-medium")
    def test_host_multiple_authors(self) -> None:
        """Test hosting multiple authors"""
        self.initialize_sample_authors(5)

        fetched_authors = LocalAuthor.objects.all()
        self.assertEqual(len(fetched_authors), 6)
