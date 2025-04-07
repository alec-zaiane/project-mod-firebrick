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
            auth=(self.other_node_user_incoming.username, "node")
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
            auth=(self.other_node_user_incoming.username, "badpassword")
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
            auth=(self.other_node_user_incoming.username, "node")
        )
        # make sure the post was not created
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_image_post(self) -> None:
        """Simulate receiving a post via node2node with an image"""
        self.receive_json["contentType"] = "image/png;base64"
        # https://gist.github.com/ondrek/7413434
        self.receive_json["content"] = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="

        receive_json_string = json.dumps(self.receive_json)

        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user_incoming.username, "node")
        )
        # make sure the post was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        # Check the post's attributes
        self.assertEqual(post.post_type, PostTypes.IMAGE)
        self.assertNotEqual(post.image, None)
        self.assertEqual(post.content, None)

    def test_create_video_post(self) -> None:
        """Simulate receiving a post via node2node with a video"""
        self.receive_json["contentType"] = "video/mp4;base64"
        # https://gist.github.com/ondrek/7413434
        self.receive_json["content"] = "AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAr9tZGF0AAACoAYF//+c3EXpvebZSLeWLNgg2SPu73gyNjQgLSBjb3JlIDEyNSAtIEguMjY0L01QRUctNCBBVkMgY29kZWMgLSBDb3B5bGVmdCAyMDAzLTIwMTIgLSBodHRwOi8vd3d3LnZpZGVvbGFuLm9yZy94MjY0Lmh0bWwgLSBvcHRpb25zOiBjYWJhYz0xIHJlZj0zIGRlYmxvY2s9MTowOjAgYW5hbHlzZT0weDM6MHgxMTMgbWU9aGV4IHN1Ym1lPTcgcHN5PTEgcHN5X3JkPTEuMDA6MC4wMCBtaXhlZF9yZWY9MSBtZV9yYW5nZT0xNiBjaHJvbWFfbWU9MSB0cmVsbGlzPTEgOHg4ZGN0PTEgY3FtPTAgZGVhZHpvbmU9MjEsMTEgZmFzdF9wc2tpcD0xIGNocm9tYV9xcF9vZmZzZXQ9LTIgdGhyZWFkcz02IGxvb2thaGVhZF90aHJlYWRzPTEgc2xpY2VkX3RocmVhZHM9MCBucj0wIGRlY2ltYXRlPTEgaW50ZXJsYWNlZD0wIGJsdXJheV9jb21wYXQ9MCBjb25zdHJhaW5lZF9pbnRyYT0wIGJmcmFtZXM9MyBiX3B5cmFtaWQ9MiBiX2FkYXB0PTEgYl9iaWFzPTAgZGlyZWN0PTEgd2VpZ2h0Yj0xIG9wZW5fZ29wPTAgd2VpZ2h0cD0yIGtleWludD0yNTAga2V5aW50X21pbj0yNCBzY2VuZWN1dD00MCBpbnRyYV9yZWZyZXNoPTAgcmNfbG9va2FoZWFkPTQwIHJjPWNyZiBtYnRyZWU9MSBjcmY9MjMuMCBxY29tcD0wLjYwIHFwbWluPTAgcXBtYXg9NjkgcXBzdGVwPTQgaXBfcmF0aW89MS40MCBhcT0xOjEuMDAAgAAAAA9liIQAV/0TAAYdeBTXzg8AAALvbW9vdgAAAGxtdmhkAAAAAAAAAAAAAAAAAAAD6AAAACoAAQAAAQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAhl0cmFrAAAAXHRraGQAAAAPAAAAAAAAAAAAAAABAAAAAAAAACoAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAgAAAAIAAAAAAAkZWR0cwAAABxlbHN0AAAAAAAAAAEAAAAqAAAAAAABAAAAAAGRbWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAAwAAAAAgBVxAAAAAAALWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAABPG1pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAAPxzdGJsAAAAmHN0c2QAAAAAAAAAAQAAAIhhdmMxAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAgACABIAAAASAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGP//AAAAMmF2Y0MBZAAK/+EAGWdkAAqs2V+WXAWyAAADAAIAAAMAYB4kSywBAAZo6+PLIsAAAAAYc3R0cwAAAAAAAAABAAAAAQAAAgAAAAAcc3RzYwAAAAAAAAABAAAAAQAAAAEAAAABAAAAFHN0c3oAAAAAAAACtwAAAAEAAAAUc3RjbwAAAAAAAAABAAAAMAAAAGJ1ZHRhAAAAWm1ldGEAAAAAAAAAIWhkbHIAAAAAAAAAAG1kaXJhcHBsAAAAAAAAAAAAAAAALWlsc3QAAAAlqXRvbwAAAB1kYXRhAAAAAQAAAABMYXZmNTQuNjMuMTA0="

        receive_json_string = json.dumps(self.receive_json)

        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user_incoming.username, "node")
        )
        # make sure the post was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        # Check the post's attributes
        self.assertEqual(post.post_type, PostTypes.VIDEO)
        self.assertNotEqual(post.video, None)
        self.assertEqual(post.content, None)
