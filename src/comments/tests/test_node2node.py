"""Tests for node2node issues"""

from django.test import tag, LiveServerTestCase, override_settings
from django.urls import reverse

from rest_framework import status

from core.utils.testing_utils import GeneralUserStoryApiTest, UITestCase

from posts.models import Post, PostTypes, VisibilityTypes
from comments.models import Comment
from user_management.models import Node, User, Author, JoinRequest

import requests


@tag("node2node")
class TestNode2Node(LiveServerTestCase):
    def setUp(self) -> None:
        self.other_node_user = User.nodes.create_user("node_other2me", password="node")
        self.other_node = Node.external_nodes.create_node(
            "other node",
            "http://localhost:10000/api",
            self.other_node_user,
            "http://localhost:10000",
        )
        super().setUp()

    @override_settings(DEBUG=True)
    def test_create_comment_via_json(self) -> None:
        """Simulate receiving a commend via node2node"""
        # create a user and a post to comment on
        author = JoinRequest.objects.create_join_request(
            "testuser", "password").approve()
        post = Post.objects.create_post(
            author,
            "My post",
            "description",
            "content",
            PostTypes.PLAINTEXT,
            VisibilityTypes.PUBLIC,
        )

        external_author = Author.external_authors.create(
            host_node=self.other_node,
            display_name="Mr External"
        )

        external_author_fqid = external_author.get_encoded_fqid()
        post_fqid = post.get_encoded_fqid()
        receive_json_string = r'{"type": "comment", "author": {"type": "author", "id": "'+external_author_fqid + \
            r'", "host": "http://localhost:10000/api", "displayName": "dev", "profileImage": "", "page": "http://localhost:10000/api/authors/3f3c2376-c0eb-401e-abd9-3a1ab6c5cfca"}, "comment": "hello", "contentType": "text/plain", "published": "2025-03-29T22:22:35.342617+00:00", "id": "http://localhost:10000/apicomments/5f4b580c-bd90-4ba1-a132-3826d3d50dec", "post": "'+post_fqid+r'", "likes": []}'
        receive_json_string = receive_json_string.replace("'", '"')
        # this is a little bit brittle, if requests gets changed in Node.send_create, etc it will need a rework
        # simulate receiving the commend via node2node
        my_url = self.live_server_url + reverse("comments:node2node_comments-list")
        response = requests.post(my_url, data=receive_json_string, headers={"Content-Type": "application/json"},
                                 auth=(self.other_node_user.username, "node"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
