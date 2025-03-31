from django.urls import reverse

from django.test import tag

import requests
from rest_framework import status

from core.utils.testing_utils import AdminUITestCase, GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author, User, Node

from user_management.forms import JoinRequestForm

from user_management.tests.mock_node import MockNode


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

    def setUp(self) -> None:
        super().setUp()
        # monkeypatch the mock nodes into the Node.external_nodes manager
        Node.external_nodes = MockNode.mock_nodes  # type: ignore

    def test_can_add_node(self) -> None:
        self.login_as_admin()

        # create the node
        self.visit("/admin/user_management/node/add/")
        self.find_element_by_id("id_name").send_keys("Other node")
        # we have to use out own node to verify validation
        self.find_element_by_id("id_host_url").send_keys("http://example.com/api")
        # connect to the user we just made
        self.find_element_by_id("id_internal_username").send_keys("user_abc")
        self.find_element_by_id("id_internal_password").send_keys("password")
        # create an external user to be connected to
        self.find_element_by_id("id_external_username").send_keys("user2_abc")
        self.find_element_by_id("id_external_password").send_keys("password")
        self.find_elements_by_selector("input[type=submit]")[0].click()

        # make sure the node was created
        self.assertEqual(Node.external_nodes.all().count(), 1)
        node_fetched = Node.external_nodes.first()
        assert node_fetched is not None  # for mypy
        self.assertEqual(node_fetched.host_url, "http://example.com/api")
        self.assertEqual(node_fetched.name, "Other node")
        assert node_fetched.internal_user is not None  # for mypy
        assert node_fetched.external_user is not None  # for mypy
        self.assertEqual(node_fetched.internal_user.username, "user_abc")
        self.assertEqual(node_fetched.internal_user.password_plain, "password")
        self.assertEqual(node_fetched.external_user.username, "user2_abc")
        self.assertEqual(node_fetched.external_user.password_plain, "password")

        self.end_test()
