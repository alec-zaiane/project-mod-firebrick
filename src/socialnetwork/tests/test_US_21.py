from unittest import skip
from django.test import tag
from django.urls import reverse

from rest_framework import status

from socialnetwork.models import PostTextBased

from .utils_for_tests import GeneralUserStoryApiTest


@skip("API changes required")
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

        self.client.force_authenticate(user=self.sample_authors[0].user)
        response = self.client.post(reverse("socialnetwork:api_textpost_create"), {
            "content": "sample post",
            "visibility": PostTextBased.VisibilityTypes.FRIENDS_ONLY
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check that the post was created, and it is friends-only
        # post_query = PostTextBased.objects.filter(...)
        # self.assertTrue(post_query.exists())
        # self.assertEqual(post_query.get().visibility_type,
        #                  PostTextBased.VisibilityTypes.FRIENDS_ONLY)
