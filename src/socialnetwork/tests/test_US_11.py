from django.test import TestCase
from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, PostTextBased
import time


class TestUserStory11(TestCase):
    """
    Test User Story 11:
    https://github.com/orgs/uofa-cmput404/projects/147/views/1?pane=issue&itemId=97853544&issue=uofa-cmput404%7Cw25-project-mod-firebrick%7C11
    As an author, I want to edit my posts locally
    Authors should be able to modify their posts without having to delete and recreate them.
    """

    def setUp(self) -> None:
        #create a user and local author
        self.user = User.objects.create_user(username="test", password="pass")
        self.author = LocalAuthor.objects.create(user=self.user)

        #create a post with some content
        self.initial_content = "This is the original post content with a typo."
        self.post = PostTextBased.objects.create(
            base_author=self.author,
            content=self.initial_content,
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC,
            post_type=PostTextBased.TextPostTypes.PLAINTEXT,
        )

    def test_edit_post_content(self) -> None:
        """Test that an author can edit their post locally without deleting it."""

        new = "This is the updated post content with the typo fixed."

        #verify the post is not edited initially
        self.assertEqual(self.post.content, self.initial_content)
        self.assertIsNone(self.post.date_edited)

        self.post.edit(new)

        #reload from DB to get updated values
        self.post.refresh_from_db()

        self.assertEqual(self.post.content, new)
        self.assertIsNotNone(self.post.date_edited)
