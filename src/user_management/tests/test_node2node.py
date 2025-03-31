"""Test the Node2Node communication for the User Management classes"""

from django.test import tag
from django.urls import reverse

from core.utils.testing_utils import GeneralUserStoryApiTest, Node2NodeReceptionTestCase

from user_management.models import FollowRequest, Author, Node, User
from user_management.tests.mock_node import MockNode, Action, ActionType, monkeypatch_mock_nodes
from posts.models import Post, PostTypes, VisibilityTypes
from comments.models import Comment
from likes.models import Like


from posts.serializers import PostSerializer
from comments.serializers import CommentSerializer
from likes.serializers import LikeSerializer
from user_management.serializers import AuthorSerializer, FollowRequestSerializer

import base64
import json
import requests


@tag("node2node")
class TestNode2NodeAuthors(GeneralUserStoryApiTest):
    """Test the Node2Node communication for Authors"""

    def test_author_detail(self) -> None:
        """Test listing a single author fits the expected format"""
        self.initialize_sample_authors(1)
        result = self.client.get(reverse("user_management:node2node_authors-detail",
                                         kwargs={"fqid": self.sample_authors[0].get_encoded_fqid()}))
        self.assertEqual(result.status_code, 200)
        expected = {
            "type": "author",
            "id": self.sample_authors[0].fqid,
            "host": self.sample_authors[0].host_node.get_host_url_slash(),
            "displayName": self.sample_authors[0].display_name,
            "profileImage": self.sample_authors[0].profile_image,
            "page": self.sample_authors[0].page_url,
        }
        self.assertEqual(result.json(), expected)

    def test_author_list(self) -> None:
        """Test listing all authors fits the expected format"""
        for author in Author.objects.all():
            author.delete()
        self.initialize_sample_authors(3)
        result = self.client.get(reverse("user_management:node2node_authors-list"))
        self.assertEqual(result.status_code, 200)
        expected = {
            "type": "authors",
            "authors": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.get_host_url_slash(),
                    "displayName": author.display_name,
                    "profileImage": author.profile_image,
                    "page": author.page_url,
                }
                for author in Author.objects.all()
            ]
        }
        self.assertEqual(result.json(), expected)

    def test_author_list_pagination(self) -> None:
        """Test listing all authors fits the expected format with pagination"""
        for author in Author.objects.all():
            author.delete()
        self.initialize_sample_authors(3)
        response = self.client.get(reverse("user_management:node2node_authors-list") + "?page=2")
        self.assertEqual(response.status_code, 404)
        response2 = self.client.get(
            reverse("user_management:node2node_authors-list") + "?page=1&size=2")
        self.assertEqual(response2.status_code, 200)
        expected2 = {
            "type": "authors",
            "authors": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.get_host_url_slash(),
                    "displayName": author.display_name,
                    "profileImage": author.profile_image,
                    "page": author.page_url,
                }
                for author in Author.objects.all()[:2]
            ]
        }
        self.assertEqual(response2.json(), expected2)
        response3 = self.client.get(
            reverse("user_management:node2node_authors-list") + "?page=2&size=2")
        self.assertEqual(response3.status_code, 200)
        expected3 = {
            "type": "authors",
            "authors": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.get_host_url_slash(),
                    "displayName": author.display_name,
                    "profileImage": author.profile_image,
                    "page": author.page_url,
                }
                for author in Author.objects.all()[2:]
            ]
        }
        self.assertEqual(response3.json(), expected3)

    def test_author_creation(self) -> None:
        """Test creating an author via the API"""
        data = {
            "type": "author",
            "id": "http://nodeaaaa.abc/api/authors/111",
            "host": "http://nodeaaaa.abc/api/",
            "displayName": "Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
            "page": "http://nodeaaaa.abc/authors/greg"
        }
        external_node_user = User.nodes.create_user("nodeaaaa", password="password")
        Node.external_nodes.create_node("Node a", "http://nodeaaaa.abc/api/", external_node_user)
        response = self.client.post(reverse("user_management:node2node_authors-list"), data)
        self.assertEqual(response.status_code, 201)
        author = Author.objects.get_by_fqid(data["id"])
        self.assertEqual(author.display_name, data["displayName"])

    def test_basic_auth(self) -> None:
        """Test that you can create an author with Http Basic Auth (so long as AuthorViewset doesn't have any special treatment it should work for all Node2Node views)"""
        data = {
            "type": "author",
            "id": "http://nodeaaaa.abc/api/authors/111",
            "host": "http://nodeaaaa.abc/api/",
            "displayName": "Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
            "page": "http://nodeaaaa.abc/authors/greg"
        }
        external_node_user = User.nodes.create_user("nodeaaaa", password="password")
        Node.external_nodes.create_node(
            name="Node a", host_url="http://nodeaaaa.abc/api/", user=external_node_user)
        # modified from https://stackoverflow.com/questions/5495452/using-basic-http-access-authentication-in-django-testing-framework
        self.client.logout()
        response = self.client.post(
            reverse("user_management:node2node_authors-list"), data,
            format="json",
            HTTP_AUTHORIZATION="Basic " + base64.b64encode(b"nodeaaaa:password").decode("utf-8"))

        self.assertEqual(response.status_code, 201)
        author = Author.objects.get_by_fqid(data["id"])
        self.assertEqual(author.display_name, data["displayName"])


@tag("node2node")
class TestNode2NodeProperSending(GeneralUserStoryApiTest):
    """Tests for whether Node2node communication is properly sent"""

    def setUp(self) -> None:
        super().setUp()
        # monkeypatch the mock nodes into the Node.external_nodes manager
        monkeypatch_mock_nodes()
    # CRUD FOR AUTHORS ========================================================

    def test_creation_of_author(self) -> None:
        """Test that when an author is created, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_authors-list')}", action)
        self.assertEqual(action.json, AuthorSerializer().to_representation(self.sample_authors[0]))

    def test_update_of_author(self) -> None:
        """Test that when an author is updated, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        node.clear_action_log()
        self.sample_authors[0].display_name = "New Name"
        self.sample_authors[0].save()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.PUT)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_authors-detail', kwargs={'fqid': self.sample_authors[0].get_encoded_fqid()})}")
        self.assertEqual(action.json, AuthorSerializer().to_representation(self.sample_authors[0]))

    def test_deletion_of_author(self) -> None:
        """Test that when an author is deleted, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        node.clear_action_log()
        self.sample_authors[0].delete()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.DELETE)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_authors-detail', kwargs={'fqid': self.sample_authors[0].get_encoded_fqid()})}")

    # CRUD FOR FOLLOW REQUESTS =================================================
    def test_creation_of_follow_request(self) -> None:
        """Test that when a follow request is created, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        external_author = Author.objects.create(host_node=node, display_name="External Author")
        self.initialize_sample_authors(2)
        node.clear_action_log()
        # author 0 follows author 1
        follow_request = FollowRequest.objects.create_follow_request(
            self.sample_authors[0], external_author)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_inbox', args=[external_author.get_encoded_fqid()])}")
        self.assertEqual(action.json, FollowRequestSerializer().to_representation(follow_request))

    # CRUD FOR POSTS ===========================================================
    def test_creation_of_post(self) -> None:
        """Test that when a post is created, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        external_author = Author.objects.create(host_node=node, display_name="External Author")
        self.initialize_sample_authors(1)
        # make external author follow the author
        external_author.following.add(self.sample_authors[0])
        # monkeypatch external_author's host_node to be the mock node
        external_author.host_node = node
        external_author.save()

        node.clear_action_log()
        post = Post.objects.create_post(
            self.sample_authors[0], "My post title", "my post description", "content", PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_inbox', args=[external_author.get_encoded_fqid()])}")
        self.assertEqual(action.json, PostSerializer().to_representation(post))

    def test_update_of_post(self) -> None:
        """Test that when a post is updated, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        post = Post.objects.create_post(
            self.sample_authors[0], "My post title", "my post description", "content", PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        node.clear_action_log()
        post.title = "New Title"
        post.visibility_type = VisibilityTypes.UNLISTED
        post.save()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.PUT)
        self.assertEqual(
            action.url, f"http://example.com{reverse('posts:api_posts-detail', kwargs={"fqid": post.get_encoded_fqid()})}")
        self.assertEqual(action.json, PostSerializer().to_representation(post))

    def test_deletion_of_post(self) -> None:
        """Test that when a post is deleted, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        post = Post.objects.create_post(
            self.sample_authors[0], "My post title", "my post description", "content", PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        node.clear_action_log()
        post.delete()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.DELETE)
        self.assertEqual(
            action.url, f"http://example.com{reverse('posts:api_posts-detail', kwargs={"fqid": post.get_encoded_fqid()})}")

    # CRUD FOR COMMENTS ========================================================

    def test_creation_of_comment(self) -> None:
        """Test that when a comment is created, the external node hosting the post's author is notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        external_author = Author.objects.create(host_node=node, display_name="External Author")
        external_post = Post.objects.create_post(
            external_author, "My post title", "my post description", "content", PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        node.clear_action_log()
        comment = Comment.objects.create_comment(
            self.sample_authors[0], external_post, "My comment", PostTypes.PLAINTEXT)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_inbox', args=[external_author.get_encoded_fqid()])}")
        self.assertEqual(action.json, CommentSerializer().to_representation(comment))

    def test_update_of_comment(self) -> None:
        """Test that when a comment is updated, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        comment = Comment.objects.create_comment(
            self.sample_authors[0], self.sample_posts[0][0], "My comment", PostTypes.PLAINTEXT)
        node.clear_action_log()
        comment.content = "New content"
        comment.save()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.PUT)
        self.assertEqual(
            action.url, f"http://example.com{reverse('comments:node2node_comments-detail', kwargs={"fqid": comment.get_encoded_fqid()})}")
        self.assertEqual(action.json, CommentSerializer().to_representation(comment))

    def test_deletion_of_comment(self) -> None:
        """Test that when a comment is deleted, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        comment = Comment.objects.create_comment(
            self.sample_authors[0], self.sample_posts[0][0], "My comment", PostTypes.PLAINTEXT)
        node.clear_action_log()
        comment.delete()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.DELETE)
        self.assertEqual(
            action.url, f"http://example.com{reverse('comments:node2node_comments-detail', kwargs={"fqid": comment.get_encoded_fqid()})}")

    # CRUD FOR LIKES ===========================================================

    def test_creation_of_like_post(self) -> None:
        """Test that when a like is created, the external node hosting the post's author is notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        external_author = Author.objects.create(host_node=node, display_name="External Author")
        external_post = Post.objects.create_post(
            external_author, "My post title", "my post description", "content", PostTypes.PLAINTEXT, VisibilityTypes.PUBLIC)
        self.initialize_sample_authors(1)
        node.clear_action_log()
        like = Like.objects.create_like(self.sample_authors[0], external_post)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_inbox', args=[external_author.get_encoded_fqid()])}")
        self.assertEqual(action.json, LikeSerializer().to_representation(like))

    def test_creation_of_like_comment(self) -> None:
        """Test that when a like is created, the external node hosting the post's author is notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        external_author = Author.objects.create(host_node=node, display_name="External Author")

        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        external_comment = Comment.objects.create_comment(
            external_author, self.sample_posts[0][0], "My comment", PostTypes.PLAINTEXT)
        node.clear_action_log()
        like = Like.objects.create_like(self.sample_authors[0], external_comment)
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.POST)
        self.assertEqual(
            action.url, f"http://example.com{reverse('user_management:node2node_inbox', args=[external_author.get_encoded_fqid()])}")
        self.assertEqual(action.json, LikeSerializer().to_representation(like))

    def test_deletion_of_like(self) -> None:
        """Test that when a like is deleted, any external nodes are notified"""
        node_user = User.nodes.create_user("node_user", password="password")
        node = MockNode.mock_nodes.create_node(name="mock_node",
                                               host_url="http://example.com/api", user=node_user)
        self.initialize_sample_authors(1)
        self.initialize_sample_text_posts(1)
        like = Like.objects.create_like(self.sample_authors[0], self.sample_posts[0][0])
        node.clear_action_log()
        like.delete()
        self.assertEqual(len(node.actions_log), 1)
        action = node.actions_log[0]
        self.assertEqual(action.action_type, ActionType.DELETE)
        self.assertEqual(
            action.url, f"http://example.com{reverse('likes:node2node_likes-detail', kwargs={"fqid": like.get_encoded_fqid()})}")


class TestNode2NodeReceiveFollowRequests(Node2NodeReceptionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.initialize_sample_authors(1)
        self.initialize_other_node()
        self.initialize_external_authors(1)
        self.author0_inbox_url = self.live_server_url + reverse("user_management:node2node_inbox", args=[
            self.sample_authors[0].get_encoded_fqid()
        ])
        self.receive_json = {
            "type": "follow",
            "summary": "A wants to follow B",
            "actor": {
                "type": "author",
                "id": self.external_authors[0].fqid,
                "host": self.other_node.get_host_url_slash(),
                "displayName": self.external_authors[0].display_name,
                "profileImage": self.external_authors[0].profile_image,
                "page": self.external_authors[0].page_url,
            },
            "object": {
                "type": "author",
                "id": self.sample_authors[0].fqid,
                "host": self.sample_authors[0].host_node.get_host_url_slash(),
                "displayName": self.sample_authors[0].display_name,
                "profileImage": self.sample_authors[0].profile_image,
                "page": self.sample_authors[0].page_url,
            }
        }

    def test_create_followrequest(self) -> None:
        """Simulate receiving a follow request from external -> local user via node2node"""
        receive_json_string = json.dumps(self.receive_json)
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user.username, "node"),
        )
        # make sure it was created
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FollowRequest.objects.count(), 1)
        follow_request = FollowRequest.objects.get()
        self.assertEqual(follow_request.follower, self.external_authors[0])
        self.assertEqual(follow_request.followee, self.sample_authors[0])
        self.assertEqual(follow_request.host_node, Node.objects.get_local_node())

    def test_create_followrequest_unauthorized(self) -> None:
        """Fail to make a follow request with invalid credentials or no credentials"""
        receive_json_string = json.dumps(self.receive_json)
        # invalid credentials
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=("invalid_user", "invalid_password"),
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(FollowRequest.objects.count(), 0)

        # no credentials
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(FollowRequest.objects.count(), 0)

    def test_create_followrequest_invalid(self) -> None:
        """Fail to make a follow request with invalid data"""
        # invalid data
        self.receive_json["type"] = "invalid"
        receive_json_string = json.dumps(self.receive_json)
        response = requests.post(
            self.author0_inbox_url,
            data=receive_json_string,
            headers={"Content-Type": "application/json"},
            auth=(self.other_node_user.username, "node"),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FollowRequest.objects.count(), 0)
