from django.test import tag
from django.urls import reverse
from core.utils.testing_utils import GeneralUserStoryApiTest, AdminUITestCase


@tag("US-Visibility")
class TestUserStory26(GeneralUserStoryApiTest):
    """
    Tests for User Story 26
    As an author, I don't want anyone except the node admin to see my deleted posts.
    """

    @tag("check-fast")
    def test_normal_user_cannot_view_deleted_post(self) -> None:
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        self.sample_posts[0][0].soft_delete()
        # log in as the normal user
        assert self.sample_authors[0].user is not None  # for mypy
        self.client.force_login(self.sample_authors[0].user)
        url = reverse("posts:view_post", kwargs={"post_uuid": self.sample_posts[0][0].uuid})
        response = self.client.get(url)
        # should get a 403 Forbidden response since the post is soft-deleted and user is not an admin
        self.assertEqual(response.status_code, 403)
        self.assertIn("do not have permission", response.content.decode())


class TestUserStory26AdminUI(AdminUITestCase):
    """
    UI tests for User Story 26
    """

    def test_admin_can_see_deleted_post(self) -> None:
        # create a post
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        self.sample_posts[0][0].soft_delete()
        # now make sure it shows up in the admin panel
        self.login_as_admin()
        self.visit("/admin/posts/post/?is_soft_deleted__exact=1")
        found_elems = self.find_elements_by_selector(f"a[href*='{self.sample_posts[0][0].uuid}']")
        self.assertEqual(len(found_elems), 1)
        self.assertEqual(found_elems[0].element.text, str(self.sample_posts[0][0].uuid))
