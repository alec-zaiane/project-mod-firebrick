from django.urls import reverse

from django.test import tag

from rest_framework import status

from core.utils.testing_utils import AdminUITestCase, GeneralUserStoryApiTest
from user_management.models import JoinRequest, Author, User, Node

from user_management.forms import JoinRequestForm


@tag("US-node-management")
class UserStory133TestUI(AdminUITestCase):
    """
    Tests for User Story 133
    "As a node admin, I want to be able to remove nodes and stop sharing with them."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/133
    """

    def test_can_remove_node(self) -> None:
        self.login_as_admin()

        # create the user of the node
        node_user = User.nodes.create_user("node_abc", password="password")

        # create the node
        node = Node.external_nodes.create_node(
            name="Other node", host_url="http://example.com/api", user=node_user)

        # make sure the node was created
        self.assertEqual(Node.external_nodes.all().count(), 1)

        # now try to delete it via the UI
        self.login_as_admin()
        self.visit(f"/admin/user_management/node/{node.uuid}/change/")
        self.find_elements_by_selector("a.deletelink")[0].click()
        self.find_elements_by_selector("input[type=submit]")[0].click()

        # make sure the node was deleted
        self.assertEqual(Node.external_nodes.all().count(), 0)

        self.end_test()
