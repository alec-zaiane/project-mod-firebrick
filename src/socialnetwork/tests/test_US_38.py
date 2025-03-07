from unittest import skip

from django.test import tag
from django.urls import reverse

from rest_framework import status

from .utils_for_tests import GeneralUserStoryApiTest, JsonGenerator

from socialnetwork import models


@tag("US-comments/likes")
class TestUserStory38(GeneralUserStoryApiTest):
    """API tests for US 38
    "As an author, I want to comment on posts that I can access, so I can make a witty reply.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/38
    """

    @tag("check-fast")
    def test_can_comment_on_post(self) -> None:
        """Test that an author can comment on a post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        comment_json = JsonGenerator.generate_comment(
            author=self.sample_authors[0],
            target=self.sample_posts[1][0],
            comment="comment",
            comment_type="text/plain")
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Comment.objects.count(), 1)
        self.assertTrue(self.sample_posts[1][0].get_comments().exists())
        comment = self.sample_posts[1][0].get_comments().get()
        self.assertEqual(comment.comment, "comment")
        self.assertEqual(getattr(comment.author, "uuid", None),
                         self.sample_authors[0].uuid)
        self.assertEqual(comment.comment_type, "text/plain")

    @tag("check-medium", "security")
    def test_cannot_comment_on_inaccessible_post(self) -> None:
        """Test that an author cannot comment on an inaccessible post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=models.Post.VisibilityTypes.FRIENDS_ONLY)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        comment_json = JsonGenerator.generate_comment(
            author=self.sample_authors[0],
            target=self.sample_posts[1][0],
            comment="comment",
            comment_type="text/plain")
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(models.Comment.objects.count(), 0)

    @skip("Remove this once Mosa's PR is merged")
    @tag("check-medium", "security")
    def test_can_comment_on_unlisted_post(self) -> None:
        """Test that an author can comment on an unlisted post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=models.Post.VisibilityTypes.UNLISTED)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("api:inbox", args=[self.sample_authors[1].uuid])
        comment_json = JsonGenerator.generate_comment(
            author=self.sample_authors[0],
            target=self.sample_posts[1][0],
            comment="comment",
            comment_type="text/plain")
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Comment.objects.count(), 1)
        self.assertTrue(self.sample_posts[1][0].get_comments().exists())
        comment = self.sample_posts[1][0].get_comments().get()
        self.assertEqual(comment.comment, "comment")
        self.assertEqual(getattr(comment.author, "uuid", None),
                         self.sample_authors[0].uuid)
        self.assertEqual(comment.comment_type, "text/plain")
