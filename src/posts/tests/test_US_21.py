from django.test import tag
from django.urls import reverse

from rest_framework import status

from posts.models import Post, VisibilityTypes

from core.utils.testing_utils import GeneralUserStoryApiTest


from unittest import skip


@skip("Not implemented")
@tag("US-Visibility")
class TestUserStory21(GeneralUserStoryApiTest):
    """
    Tests for User Story 21
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/21
    As an author, I want to be able to make my posts "friends-only," so that I don't have to worry about people I don't know seeing them.
    """

    @tag("check-fast")
    def test_make_post_friends_only(self) -> None:
        """Test that an author can make a post friends-only"""
        self.initialize_sample_authors(1)

        # TODO
