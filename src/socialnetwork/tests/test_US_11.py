from django.test import tag
from django.urls import reverse
from rest_framework.test import APITestCase
from socialnetwork.models import PostTextBased, Post
from .utils_for_tests import GeneralUserStoryApiTest


@tag("US-Posting")
class TestUserStory11(GeneralUserStoryApiTest):
    """
    Test User Story 11:
    As an author, I want to edit my posts locally using the API.
    """

    @tag("check-fast")
    def test_edit_post_content_via_api(self) -> None:
        """Test that an author can edit their post locally using the API."""

        #init author and a Post
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(posts_per_author=1)

        author = self.sample_authors[0]

        #get first Post
        post = self.sample_posts[0][0]

        initial_content = post.content
        new_content = "This is the updated post content with the typo fixed."


        self.assertEqual(post.content, initial_content)

        #authenticate as the post's author
        self.client.force_authenticate(user=author.user)

        #call api to edit the Post
        url = reverse("socialnetwork:api_textpost_update", args=[post.uuid])
        response = self.client.post(url, {"content": new_content}, format="json")

        #check response
        self.assertEqual(response.status_code, 200)

        #reload the post from DB
        post.refresh_from_db()

        self.assertEqual(post.content, new_content)
