from django.test import tag
from django.urls import reverse
from rest_framework.test import APITestCase
from socialnetwork.models import PostTextBased, Post
from .utils_for_tests import GeneralUserStoryApiTest


@tag("US-visibility")
class TestUserStory_UnlistedPublicPosts(GeneralUserStoryApiTest):
    """
    Tests for User Story:
    https://github.com/orgs/uofa-cmput404/projects/147/views/1?pane=issue&itemId=97855322&issue=uofa-cmput404%7Cw25-project-mod-firebrick%7C24
    As an author, I want everyone to be able to see my public and unlisted posts, if they have a link to it.
    """

    @tag("check-fast")
    def test_public_post_accessible_by_anyone(self) -> None:
        """Test that public posts are accessible by anyone via URL."""

        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1, visibility_type=Post.VisibilityTypes.PUBLIC)

        #get url of public post
        public_post = self.sample_posts[0][0]  #first authors first post
        response = self.client.get(reverse("api:post_retrieve", args=[public_post.uuid]))
        
        #should be visible
        self.assertEqual(response.status_code, 200)

    @tag("check-fast")
    def test_unlisted_post_accessible_via_url(self) -> None:
        """Test that unlisted posts are accessible if you have the link."""

        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1, visibility_type=Post.VisibilityTypes.UNLISTED)

        #get url of the unlisted post
        unlisted_post = self.sample_posts[0][0]

        response = self.client.get(reverse("api:post_retrieve", args=[unlisted_post.uuid]))

        #should be visible
        self.assertEqual(response.status_code, 200)