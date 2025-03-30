from django.test import tag
from django.urls import reverse

from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest

from comments.models import Comment
from posts.models import PostTypes, VisibilityTypes
from likes.models import Like

from user_management.serializers import AuthorSerializer

from urllib.parse import quote


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
        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].get_encoded_fqid()])
        like_json = {
            "type": "like",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "published": "2021-10-10T10:00:00Z",
            "id": "http://nodeaaaa.com/api/authors/111/liked/166",
            "object": quote(self.sample_posts[0][0].fqid, safe="")
        }

        response = self.client.post(
            url, like_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.sample_posts[0][0].refresh_from_db()
        self.assertEqual(self.sample_posts[0][0].likes.count(), 1)
        first_like = self.sample_posts[0][0].likes.first()
        assert first_like is not None  # for mypy
        assert first_like.author is not None  # for mypy
        self.assertEqual(first_like.author.uuid, self.sample_authors[0].uuid)

    @tag("check-slow", "security")
    def test_cannot_like_inaccessible_post(self) -> None:
        """Test that an author cannot like a post they cannot access"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.FRIENDS_ONLY)

        self.client.force_authenticate(user=self.sample_authors[1].user)
        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].get_encoded_fqid()])
        like_json = {
            "type": "like",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "published": "2021-10-10T10:00:00Z",
            "id": "http://nodeaaaa.com/api/authors/111/liked/166",
            "object": quote(self.sample_posts[0][0].fqid, safe="")
        }

        response = self.client.post(
            url, like_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.sample_posts[0][0].refresh_from_db()
        self.assertEqual(self.sample_posts[0][0].likes.count(), 0)
        self.assertEqual(Like.objects.count(), 0)

    @tag("check-fast")
    def test_can_like_comment(self) -> None:
        """Test that an author can like a comment"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        # author 1 comments on author 0's post, then author 0 likes the comment

        comment = Comment.objects.create_comment(
            author=self.sample_authors[1],
            post=self.sample_posts[0][0],
            content="Comment",
            content_type=PostTypes.PLAINTEXT
        )

        url = reverse("user_management:node2node_inbox", args=[
                      self.sample_authors[1].get_encoded_fqid()])
        self.client.force_authenticate(user=self.sample_authors[0].user)
        like_json = {
            "type": "like",
            "author": AuthorSerializer().to_representation(self.sample_authors[0]),
            "published": "2021-10-10T10:00:00Z",
            "id": "http://nodeaaaa.com/api/authors/111/liked/166",
            "object": quote(comment.fqid, safe="")
        }
        self.client.post(url, like_json, format="json")
        comment.refresh_from_db()
        self.assertEqual(comment.likes.count(), 1)
        first_like = comment.likes.first()
        assert first_like is not None  # for mypy
        self.assertEqual(first_like.author.uuid, self.sample_authors[0].uuid)
        self.assertEqual(first_like.target.uuid, comment.uuid)
