from django.test import tag
from django.urls import reverse
from unittest import skip

from rest_framework import status

from .utils_for_tests import GeneralUserStoryApiTest, JsonGenerator

from socialnetwork import models


@tag("US-comments/likes")
class TestUserStory39(GeneralUserStoryApiTest):
    """
    API Tests for user story 39
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/39
    "As an author, I want to like posts that I can access, so I can show my appreciation."
    """

    @tag("check-fast")
    def test_can_like_post(self) -> None:
        """Test that an author can like a post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        like_json = JsonGenerator.generate_like(
            self.sample_authors[0], self.sample_posts[1][0])

        response = self.client.post(
            url, like_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_post_ref = models.PostTextBased.objects.get(
            uuid=self.sample_posts[1][0].uuid)
        self.assertEqual(new_post_ref.get_likes().count(), 1)
        first_like = new_post_ref.get_likes().first()
        assert first_like is not None  # for mypy
        assert first_like.author is not None  # for mypy
        self.assertEqual(first_like.author.uuid, self.sample_authors[0].uuid)

    @tag("check-slow", "security")
    def test_cannot_like_inaccessible_post(self) -> None:
        """Test that an author cannot like a post they cannot access"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=models.PostTextBased.VisibilityTypes.FRIENDS_ONLY)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        like_json = JsonGenerator.generate_like(
            self.sample_authors[0], self.sample_posts[1][0])
        response = self.client.post(
            url, like_json, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(models.Like.objects.count(), 0)
        self.assertEqual(models.PostTextBased.objects.get(
            uuid=self.sample_posts[1][0].uuid).get_likes().count(), 0)

    @tag("check-slow", "security")
    @skip("Waiting for implmentation of following")
    def test_can_like_friends_only_post_if_friends(self) -> None:
        """Test that an author can like a friends-only post if they are friends"""
        ...

    @tag("check-fast")
    def test_can_like_comment(self) -> None:
        """Test that an author can like a comment"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        # send a comment
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        comment_json = JsonGenerator.generate_comment(
            author=self.sample_authors[0],
            target=self.sample_posts[1][0],
            comment="comment",
            comment_type="text/plain")
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = models.PostTextBased.objects.get(
            uuid=self.sample_posts[1][0].uuid)
        comment = post.get_comments().first()
        assert comment is not None  # for mypy

        # send a like
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        like_json = JsonGenerator.generate_like(
            self.sample_authors[0], comment)
        response = self.client.post(url, like_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # verify the like
        self.assertEqual(models.Like.objects.count(), 1)
        like = models.Like.objects.first()
        assert like is not None  # for mypy
        assert like.author is not None  # for mypy
        self.assertEqual(like.author.uuid, self.sample_authors[0].uuid)

    @tag("check-slow", "security")
    @skip("Waiting for implmentation of comments")
    def test_cannot_like_inaccessible_comment(self) -> None:
        """Test that an author cannot like a comment they cannot access"""
        ...

    @tag("check-slow", "security")
    @skip("Waiting for implmentation of comments")
    def test_can_like_friends_only_comment_if_allowed(self) -> None:
        """Test that an author can like a friends-only comment if they are allowed to"""
        ...
