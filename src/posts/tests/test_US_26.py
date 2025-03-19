from django.test import tag
from django.urls import reverse
from posts.models import Post, PostTypes, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest
from user_management.models import Author


@tag("US-Visibility")
class TestUserStory26(GeneralUserStoryApiTest):
    """
    Tests for User Story 26
    As an author, I don't want anyone except the node admin to see my deleted posts.
    """
    def setUp(self) -> None:
        super().setUp()
        # create local authors
        self.admin_author = Author.local_authors.create_author(
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            display_name="Admin Author",
            is_superuser=True  
        )
        self.normal_author = Author.local_authors.create_author(
            username="normal",
            password="normalpassword",
            email="normal@example.com",
            display_name="Normal Author"
        )
        # create a post by the normal author
        self.post = Post.objects.create_post(
            author=self.normal_author,
            title="Test Post",
            description="Test Description",
            content="Test Content",
            post_type=PostTypes.PLAINTEXT,
            visibility_type=VisibilityTypes.PUBLIC
        )

        self.post.soft_delete()

    @tag("check-fast")
    def test_normal_user_cannot_view_deleted_post(self) -> None:
        # log in as the normal user
        self.client.login(username="normal", password="normalpassword")
        url = reverse("posts:view_post", kwargs={"post_uuid": self.post.uuid})
        response = self.client.get(url)
        # should get a 403 Forbidden response since the post is soft-deleted and user is not an admin
        self.assertEqual(response.status_code, 403)
        self.assertIn("do not have permission", response.content.decode())

    @tag("check-fast")
    def test_admin_can_view_deleted_post(self) -> None:
        # log in as the admin user
        self.client.login(username="admin", password="adminpassword")
        url = reverse("posts:view_post", kwargs={"post_uuid": self.post.uuid})
        response = self.client.get(url)
        # admin should be able to view the soft-deleted post
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post.title, response.content.decode())
