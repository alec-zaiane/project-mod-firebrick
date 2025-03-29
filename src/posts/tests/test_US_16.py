from django.test import tag
from django.urls import reverse

from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-posting")
class TestUserStory16(GeneralUserStoryApiTest):
    """
    Tests for User Story 16
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/16
    As an author, other authors cannot modify my posts
    """

    @tag("check-fast", "security")
    def test_cannot_modify_post(self) -> None:
        """Test that an author cannot modify posts of another author"""
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)

        # try to modify the post of another author
        url = reverse("posts:edit_post", args=[
                      self.sample_posts[0][0].uuid])

        self.client.force_authenticate(user=self.sample_authors[1].user)
        assert self.sample_authors[1].user is not None
        self.client.force_login(self.sample_authors[1].user)
        post = self.sample_posts[0][0]
        updated_post = {
            "title": post.title,
            "description": post.description,
            "content": "My new content",
            "post_type": post.post_type,
            "visibility_type": post.visibility_type,
        }
        response = self.client.put(url, updated_post, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(post.content, updated_post["content"])
