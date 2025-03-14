from typing import Any

from django.test import tag

from user_management.models import Author, JoinRequest, User
from core.utils.testing_utils import AdminUITestCase


# @skip("Not implemented")
@tag("US-node-management", "ui")
class TestUserStory44(AdminUITestCase):
    # TODO refactor into a UI test!
    """
    Tests for User Story 44
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/44
    "As a node admin, I want to be able to add, modify, and delete authors"
    """

    @tag("check-slow")
    def test_add_author(self) -> None:
        """Test adding an author"""
        self.login_as_admin()
        # create a join request
        self.log("Creating join request")
        self.visit("/admin/user_management/joinrequest/add")
        self.find_element_by_name("username").send_keys("new_author")
        self.find_element_by_name("display_name").send_keys("New Author")
        self.find_element_by_name("password").send_keys("passwordlong")
        self.find_element_by_name("_save").click()
        join_request = JoinRequest.objects.get_join_request("new_author")
        self.log(f"Created join request, uuid: {join_request.uuid}")

        join_request.approve()

        self.assertFalse(
            JoinRequest.objects.filter(uuid=join_request.uuid).exists()
        )
        self.assertTrue(
            Author.objects.filter(
                _user__username="new_author").exists()
        )
        self.end_test()

    @tag("check-slow")
    def test_fail_on_add_existing_username(self) -> None:
        """Test that you cannot add another author with the same username"""
        self.login_as_admin()
        # create a join request
        join_request = JoinRequest.objects.create_join_request(
            "new_author", display_name="New Author", password="passwordlong")
        # approve it
        join_request.approve()
        # add another one with the same username (via the UI)
        self.log("Creating duplicate join request")
        self.visit("/admin/user_management/joinrequest/add")
        self.find_element_by_name("username").send_keys("new_author")
        self.find_element_by_name("display_name").send_keys("New Author")
        self.find_element_by_name("password").send_keys("passwordlong")
        self.find_element_by_name("_save").click()
        join_request_2 = JoinRequest.objects.get_join_request("new_author")
        # try to approve it...
        self.visit("/admin/user_management/joinrequest/")
        self.find_elements_by_value(str(join_request_2.uuid))[0].click()
        self.adminpanel_do_action("Approve selected join requests")
        # ...and make sure it fails
        messages = self.find_elements_by_selector("ul.messagelist")
        self.assertIn("is already taken", messages[0].element.text)
        self.assertEqual(JoinRequest.objects.filter(username="new_author").count(), 1)
        self.end_test()

    @tag("check-slow")
    def test_modify_author(self) -> None:
        """Test modifying the sample authors for success"""
        self.login_as_admin()

        # list of updates to be made on the sample authors
        # each update is a tuple of the form ((field_name, new_value), (prop_name, expected_value))
        updates: list[tuple[tuple[str, str], tuple[str, str]]] = [
            (("username", "new_username"), ("username", "new_username")),                    # noqa
            (("display_name", "new_display_name"), ("display_name", "new_display_name")),    # noqa
            (("profile_image", "https://picsum.photos/200"), ("profile_image", "https://picsum.photos/200")),  # noqa
            (("bio", "new_bio"), ("bio", "new_bio"))                                         # noqa
        ]

        # create new sample authors, one for each update to try
        self.log(f"Creating {len(updates)} sample authors")
        self.initialize_sample_authors(len(updates))

        def getattr_nested(obj: Any, attr: str) -> Any:
            for a in attr.split("."):
                obj = getattr(obj, a)
            return obj

        for ((field_name, new_value), (prop_name, expected_value)), author in zip(updates, self.sample_authors):
            # for each update, try to edit that author in the UI, and make sure it worked
            self.assertNotEqual(
                getattr_nested(author, prop_name),
                expected_value,
                f"Author {author.uuid} already has {prop_name} == {expected_value}"
            )
            self.visit(f"/admin/user_management/author/{author.uuid}/change/")
            self.find_element_by_name(field_name).clear()
            self.find_element_by_name(field_name).send_keys(new_value)
            self.find_element_by_name("_save").click()
            author.refresh_from_db()
            self.assertEqual(
                getattr_nested(author, prop_name),
                expected_value,
                f"Author {author.uuid} does not have {prop_name} == {expected_value} post-update"
            )
        self.end_test()

    @tag("check-slow")
    def test_modify_author_fail_on_double_username(self) -> None:
        """Test if updating a user to have the same username as another fails as expected"""
        self.initialize_sample_authors(2)
        self.login_as_admin()
        # try to update the first author to have the same username as the second
        author_1 = self.sample_authors[0]
        author_2 = self.sample_authors[1]
        self.visit(f"/admin/user_management/author/{author_1.uuid}/change/")
        self.find_element_by_name("username").clear()
        self.find_element_by_name("username").send_keys(author_2.username)
        self.find_element_by_name("_save").click()
        self.assert_path(f"/admin/user_management/author/{author_1.uuid}/change/")
        messages = self.find_elements_by_selector("ul.errorlist")
        self.assertIn("is already taken", messages[0].element.text)
        author_1.refresh_from_db()
        self.assertNotEqual(author_1.username, author_2.username)
        self.end_test()

    @tag("check-slow")
    def test_delete_author(self) -> None:
        """Test that deleting a single author works"""
        self.login_as_admin()
        self.log("Creating sample author")
        self.initialize_sample_authors(1)
        author = self.sample_authors[0]
        self.log("Deleting sample author via UI")
        self.visit(f"/admin/user_management/author/{author.uuid}/delete/")
        self.find_elements_by_selector("input[type=submit]")[0].click()
        self.assertFalse(Author.objects.filter(uuid=author.uuid).exists())
        self.assertFalse(User.objects.filter(username=author.username).exists())
        self.end_test()

    @tag("check-slow")
    def test_delete_multiple_authors(self) -> None:
        """Test that deleting multiple authors works"""
        self.login_as_admin()
        self.log("Creating sample authors")
        self.initialize_sample_authors(2)
        authors = self.sample_authors
        self.log("Deleting sample authors via UI")
        self.visit("/admin/user_management/author/")
        for author in authors:
            self.find_elements_by_value(str(author.uuid))[0].click()
        self.adminpanel_do_action("Delete selected authors", confirm_needed=True)
        self.visit("/admin/user_management/author/")  # delay to let the deletion happen
        self.assertFalse(Author.objects.filter(uuid=authors[0].uuid).exists())
        self.assertFalse(User.objects.filter(username=authors[0].username).exists())
        self.assertFalse(Author.objects.filter(uuid=authors[1].uuid).exists())
        self.assertFalse(User.objects.filter(username=authors[1].username).exists())
        self.end_test()
