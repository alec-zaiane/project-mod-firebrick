from django.urls import reverse

from django.test import tag

from rest_framework import status

from core.utils.testing_utils import AdminUITestCase, GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author, User, Node

from user_management.forms import JoinRequestForm
from user_management.tests.mock_node import MockNode


@tag("US-node-management")
class UserStory132TestUI(AdminUITestCase):
    """
    Tests for User Story 136
    "As a node admin, I can disable the node to node interfaces for connections that I no longer want, in case another node goes bad.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/136
    """

    def setUp(self) -> None:
        super().setUp()
        # monkeypatch the mock nodes into the Node.external_nodes manager
        Node.external_nodes = MockNode.mock_nodes  # type: ignore

    def test_can_disable_node(self) -> None:
        self.login_as_admin()

        # create the user of the node
        node_user = User.nodes.create_user("node_abc", password="password")

        # create the node
        node = MockNode.mock_nodes.create_node(
            name="mock node", host_url="http://example.com/api", user=node_user)

        # make sure the node was created
        self.assertEqual(Node.external_nodes.all().count(), 1)

        # now try to disable it via the UI
        self.login_as_admin()
        self.visit(f"/admin/user_management/node/{node.uuid}/change/")
        self.find_element_by_id("id_is_disabled").click()
        self.find_elements_by_selector("input[type=submit]")[0].click()

        # make sure the node was disabled
        node.refresh_from_db()
        self.assertTrue(node.is_disabled)

        self.assertEqual(Node.objects.count(), 2)  # local + this one

        # make sure it doesn't show up in the external nodes
        self.assertEqual(Node.external_nodes.all().count(), 0)

        self.end_test()
