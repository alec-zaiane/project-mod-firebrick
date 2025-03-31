from django.urls import reverse

from rest_framework import status

from core.utils.testing_utils import Node2NodeReceptionTestCase

from posts.models import Post, PostTypes, VisibilityTypes

import requests

import json


class TestNode2NodePosts(Node2NodeReceptionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.initialize_sample_authors(1)
        self.initialize_other_node()

        self.initialize_external_authors(1)

        self.author0_inbox_url = self.live_server_url + reverse("user_management:node2node_inbox", args=[
            self.sample_authors[0].uuid
        ])

        external_author = self.external_authors[0]
        self.receive_json = {
            "type": "post",
            "title": "Test Post",
            "id": "http://localhost:10000/api/posts/12345",
            "page": "http://localhost:10000/posts/12345",
            "description": "Test description",
            "contentType": "text/plain",
            "content": "Test content",
            "author": {
                "type": "author",
                "id": external_author.fqid,
                "host": self.other_node.get_host_url_slash(),
                "displayName": external_author.display_name,
                "profileImage": "",
                "page": "http://localhost:10000/api/authors/3f3c2376-c0eb-401e-abd9-3a1ab6c5cfca",
            },
            "comments": {
                "type": "comments",
                "id": "http://localhost:10000/api/authors/3f3c2376-c0eb-401e-abd9-3a1ab6c5cfca/posts/12345/comments",
                "page": "http://localhost:10000/posts/12345/comments",
                "page_number": 1,
                "size": 5,
                "count": 0,
                "src": [],
            },
            "likes": {
                "type": "likes",
                "id": "http://localhost:10000/api/authors/3f3c2376-c0eb-401e-abd9-3a1ab6c5cfca/posts/12345/likes",
                "page": "http://localhost:10000/posts/12345/likes",
                "page_number": 1,
                "size": 50,
                "count": 0,
                "src": [],
            },
            "published": "2025-03-29T22:22:35.342617+00:00",
            "visibility": "FRIENDS"
        }

    def test_create_post_via_json(self) -> None:
        """Simulate receiving a post via node2node"""

        receive_json_string = json.dumps(self.receive_json)

        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user.username, "node")
        )
        # make sure the post was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        # Check the post's attributes
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.description, "Test description")
        self.assertEqual(post.content, "Test content")
        self.assertEqual(post.post_type, PostTypes.PLAINTEXT)
        self.assertEqual(post.visibility_type, VisibilityTypes.FRIENDS_ONLY)
        self.assertEqual(post.author, self.external_authors[0])
        self.assertEqual(post.comments.count(), 0)
        self.assertEqual(post.likes.count(), 0)
        self.assertEqual(post.fqid, "http://localhost:10000/api/posts/12345")

    def test_create_post_unauthorized(self) -> None:
        """Simulate receiving a post via node2node with invalid/missing auth"""
        receive_json_string = json.dumps(self.receive_json)

        # try with bad auth
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user.username, "badpassword")
        )
        # make sure the post was not created
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        self.assertEqual(Post.objects.count(), 0)

        # try without auth
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
        )
        # make sure the post was not created
        self.assertIn(response.status_code, [
                      status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        self.assertEqual(Post.objects.count(), 0)

    def test_create_post_with_invalid_data(self) -> None:
        """Simulate receiving a post via node2node"""

        self.receive_json["type"] = "invalid_type"
        self.receive_json["published"] = "invalid_date"
        receive_json_string = json.dumps(self.receive_json)

        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user.username, "node")
        )
        # make sure the post was not created
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)
