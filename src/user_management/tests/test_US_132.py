from django.urls import reverse

from django.test import tag

from rest_framework import status

from core.utils.testing_utils import AdminUITestCase, GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author, User, Node

from user_management.forms import JoinRequestForm


@tag("US-node-management")
class UserStory132Test(GeneralUserStoryApiTest):
    """
    Tests for User Story 132
    "As a node admin, I want to be able to add nodes to share with."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/132
    """

    def test_can_add_node(self) -> None:
        node_user = User.nodes.create_user("node_abc", password="password")
        node = Node.external_nodes.create_node("Other node", "http://example.com/api", node_user)

        self.assertEqual(Node.external_nodes.all().count(), 1)
        self.assertEqual(Node.external_nodes.first(), node)
        node_fetched = Node.external_nodes.first()
        assert node_fetched is not None  # for mypy
        self.assertEqual(node_fetched.host_url, "http://example.com/api")


@tag("US-node-management")
class UserStory132TestUI(AdminUITestCase):
    """
    Tests for User Story 132
    "As a node admin, I want to be able to add nodes to share with."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/132
    """

    def test_can_add_node(self) -> None:
        self.login_as_admin()

        # create the user of the node
        self.visit("/admin/user_management/user/add/")
        self.find_element_by_id("id_password").send_keys("password")
        self.find_element_by_id("id_username").send_keys("node_abc")
        self.find_element_by_id("id_type").as_selector_choose_value("Node")
        self.find_elements_by_selector("input[type=submit]")[0].click()

        # create the node
        self.visit("/admin/user_management/node/add/")
        self.find_element_by_id("id_name").send_keys("Other node")
        self.find_element_by_id("id_host_url").send_keys("http://example.com/api")
        self.find_element_by_id("id_internal_user").as_selector_choose_value("node_abc")
        self.find_elements_by_selector("input[type=submit]")[0].click()

        # make sure the node was created
        self.assertEqual(Node.external_nodes.all().count(), 1)
        node_fetched = Node.external_nodes.first()
        assert node_fetched is not None  # for mypy
        self.assertEqual(node_fetched.host_url, "http://example.com/api")
        self.assertEqual(node_fetched.name, "Other node")
        assert node_fetched.internal_user is not None  # for mypy
        self.assertEqual(node_fetched.internal_user.username, "node_abc")

        self.end_test()
