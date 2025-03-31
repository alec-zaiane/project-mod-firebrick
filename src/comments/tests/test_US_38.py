
from django.test import tag
from django.urls import reverse

from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest, UITestCase

from posts.models import VisibilityTypes
from comments.models import Comment
from user_management.serializers import AuthorSerializer
from user_management.models import Node


@tag("US-comments/likes")
class TestUserStory38(GeneralUserStoryApiTest):
    """API tests for US 38
    "As an author, I want to comment on posts that I can access, so I can make a witty reply.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/38
    """

    @tag("check-fast")
    def test_can_comment_on_post(self) -> None:
        """Test that an author can comment on a post via the API"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].uuid])
        comment_json = {
            "type": "comment",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "comment": "Comment",
            "contentType": "text/plain",
            "published": "2021-03-01T00:00:00Z",
            "id": f"{Node.objects.get_local_node().host_url}/comments/1",
            "post": self.sample_posts[1][0].fqid,
        }
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(self.sample_posts[1][0].comments.exists())
        comment = self.sample_posts[1][0].comments.get()
        self.assertEqual(comment.content, "Comment")
        self.assertEqual(getattr(comment.author, "uuid", None),
                         self.sample_authors[0].uuid)

    @tag("check-medium", "security")
    def test_cannot_comment_on_inaccessible_post(self) -> None:
        """Test that an author cannot comment on an inaccessible post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.FRIENDS_ONLY)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].uuid])
        comment_json = {
            "type": "comment",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "comment": "Comment",
            "contentType": "text/plain",
            "published": "2021-03-01T00:00:00Z",
            "id": f"{Node.objects.get_local_node().host_url}/comments/1",
            "post": self.sample_posts[1][0].fqid,
        }
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)

    @tag("check-medium", "security")
    def test_can_comment_on_unlisted_post(self) -> None:
        """Test that an author can comment on an unlisted post"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.UNLISTED)

        self.client.force_authenticate(user=self.sample_authors[0].user)
        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].uuid])
        comment_json = {
            "type": "comment",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "comment": "Comment",
            "contentType": "text/plain",
            "published": "2021-03-01T00:00:00Z",
            "id": f"{Node.objects.get_local_node().host_url}/comments/1",
            "post": self.sample_posts[1][0].fqid,
        }
        response = self.client.post(url, comment_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(self.sample_posts[1][0].comments.exists())
        comment = self.sample_posts[1][0].comments.get()
        self.assertEqual(comment.content, "Comment")
        self.assertEqual(getattr(comment.author, "uuid", None),
                         self.sample_authors[0].uuid)


class TestUserStory38UI(UITestCase):
    """UI tests for US 38
    "As an author, I want to comment on posts that I can access, so I can make a witty reply.
    """

    def test_can_comment_on_post(self) -> None:
        """Test that an author can comment on a post via the UI"""
        self.skip_if_on_github_actions()
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        self.login_as(self.sample_authors[0])

        # make a comment
        self.visit(reverse("posts:view_post", args=[self.sample_posts[1][0].uuid]))
        self.find_element_by_id("add-comment-area").send_keys("My cool comment")
        self.find_element_by_id("submit-comment").click()
        self.visit(reverse("posts:view_post", args=[self.sample_posts[1][0].uuid]))
        # make sure it exists
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        assert comment is not None  # for mypy
        self.assertEqual(comment.content, "My cool comment")
        self.assertEqual(comment.author.uuid, self.sample_authors[0].uuid)
        # make sure it is rendered
        comment_card = self.find_element_by_id(f"comment-{comment.uuid}")
        self.assertIn("My cool comment", comment_card.element.text)
        self.end_test()
