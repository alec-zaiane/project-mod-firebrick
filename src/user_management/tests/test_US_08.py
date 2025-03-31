from django.test import tag
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from core.utils.testing_utils import GeneralUserStoryApiTest
from posts.models import Post, VisibilityTypes


@tag("US-reading")
class TestProfilePublicPosts(GeneralUserStoryApiTest):
    """
    Tests for User Story 08:
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/8
    As an author, I want my profile page to show my public posts (most recent first), so they can decide if they want to follow me.
    """

    def setUp(self) -> None:
        """
        Set up test data
        """
        super().setUp()
        # create authors
        self.initialize_sample_authors(2)
        self.profile_owner = self.sample_authors[0]
        self.viewer = self.sample_authors[1]

        # create oldest public post
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.PUBLIC,
        )
        self.oldest_public = Post.objects.filter(
            author=self.profile_owner, visibility_type=VisibilityTypes.PUBLIC
        ).first()
        if self.oldest_public is None:
            raise ValueError("Failed to create oldest public post")
        self.oldest_public.created_at = timezone.now() - timedelta(days=2)
        self.oldest_public.save()

        # create newest public post
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.PUBLIC,
        )
        self.newest_public = (
            Post.objects.filter(
                author=self.profile_owner, visibility_type=VisibilityTypes.PUBLIC
            )
            .order_by("-created_at")
            .first()
        )
        if self.newest_public is None:
            raise ValueError("Failed to create newest public post")
        # create friends-only post
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.FRIENDS_ONLY,
        )
        self.friends_post = Post.objects.filter(
            author=self.profile_owner, visibility_type=VisibilityTypes.FRIENDS_ONLY
        ).first()
        if self.friends_post is None:
            raise ValueError("Failed to create friends-only post")

        # create unlisted post
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.UNLISTED,
        )
        self.unlisted_post = Post.objects.filter(
            author=self.profile_owner, visibility_type=VisibilityTypes.UNLISTED
        ).first()
        if self.unlisted_post is None:
            raise ValueError("Failed to create unlisted post")

    def test_profile_shows_only_public_posts(self) -> None:
        """
        Test that profile only shows public posts
        """
        response = self.client.get(
            reverse("user_management:author_profile", args=[self.profile_owner.uuid])
        )

        self.assertEqual(response.status_code, 200)
        posts = response.context["posts"]

        # should show public posts
        self.assertIn(self.newest_public, posts)
        self.assertIn(self.oldest_public, posts)
        # should not show non-public posts
        self.assertNotIn(self.friends_post, posts)
        self.assertNotIn(self.unlisted_post, posts)

    def test_posts_ordered_most_recent_first(self) -> None:
        """
        Test that posts are ordered with newest first
        """

        response = self.client.get(
            reverse("user_management:author_profile", args=[self.profile_owner.uuid])
        )

        self.assertEqual(response.status_code, 200)
        posts = list(response.context["posts"])

        # first post should be newest
        self.assertEqual(posts[0], self.newest_public)
        # second post should be oldest
        self.assertEqual(posts[1], self.oldest_public)

    def test_other_authors_posts_not_shown(self) -> None:
        """
        Test that only profile owner's posts are shown
        """
        # create post by different author
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.PUBLIC,
        )
        other_author_post = Post.objects.filter(
            author=self.viewer, visibility_type=VisibilityTypes.PUBLIC
        ).first()
        response = self.client.get(
            reverse("user_management:author_profile", args=[self.profile_owner.uuid])
        )

        self.assertEqual(response.status_code, 200)
        posts = response.context["posts"]

        self.assertNotIn(
            other_author_post,
            posts,
            "Other authors' posts should not appear on profile",
        )

    def test_unauthenticated_user_can_view_public_posts(self) -> None:
        """
        Test that unauthenticated users can view public posts
        """
        # simulate unauthenticated user
        self.client.logout()

        response = self.client.get(
            reverse("user_management:author_profile", args=[self.profile_owner.uuid])
        )

        self.assertEqual(response.status_code, 200)
        posts = response.context["posts"]

        # should show public posts
        self.assertIn(self.newest_public, posts)
        self.assertIn(self.oldest_public, posts)
        # should not show non-public posts
        self.assertNotIn(self.friends_post, posts)
        self.assertNotIn(self.unlisted_post, posts)

    def test_post_content_visible(self) -> None:
        """
        Test that post content is visible and readable
        """
        test_content = "Test public post content"
        test_title = "Test Post Title"

        # create post with specific content
        self.initialize_sample_text_posts(
            posts_per_author=1,
            visibility_type=VisibilityTypes.PUBLIC,
        )
        test_post = (
            Post.objects.filter(
                author=self.profile_owner, visibility_type=VisibilityTypes.PUBLIC
            )
            .order_by("-created_at")
            .first()
        )
        if test_post is None:
            raise ValueError("Failed to create test post")
        test_post.content = test_content
        test_post.title = test_title
        test_post.save()

        response = self.client.get(
            reverse("user_management:author_profile", args=[self.profile_owner.uuid])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_content)
        self.assertContains(response, test_title)
