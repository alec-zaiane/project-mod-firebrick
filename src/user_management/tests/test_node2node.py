"""Test the Node2Node communication for the User Management classes"""

from django.test import tag
from django.urls import reverse

from core.utils.testing_utils import GeneralUserStoryApiTest

from user_management.models import FollowRequest, Author, Node


@tag("node2node")
class TestNode2NodeAuthors(GeneralUserStoryApiTest):
    """Test the Node2Node communication for Authors"""

    def test_author_detail(self) -> None:
        """Test listing a single author fits the expected format"""
        self.initialize_sample_authors(1)
        result = self.client.get(reverse("user_management:author-detail",
                                         args=[str(self.sample_authors[0].uuid)]))
        self.assertEqual(result.status_code, 200)
        expected = {
            "type": "author",
            "id": self.sample_authors[0].fqid,
            "host": self.sample_authors[0].host_node.host_url,
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
        result = self.client.get(reverse("user_management:author-list"))
        self.assertEqual(result.status_code, 200)
        expected = {
            "type": "authors",
            "items": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.host_url,
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
        response = self.client.get(reverse("user_management:author-list") + "?page=2")
        self.assertEqual(response.status_code, 404)
        response2 = self.client.get(reverse("user_management:author-list") + "?page=1&size=2")
        self.assertEqual(response2.status_code, 200)
        expected2 = {
            "type": "authors",
            "items": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.host_url,
                    "displayName": author.display_name,
                    "profileImage": author.profile_image,
                    "page": author.page_url,
                }
                for author in Author.objects.all()[:2]
            ]
        }
        self.assertEqual(response2.json(), expected2)
        response3 = self.client.get(reverse("user_management:author-list") + "?page=2&size=2")
        self.assertEqual(response3.status_code, 200)
        expected3 = {
            "type": "authors",
            "items": [
                {
                    "type": "author",
                    "id": author.fqid,
                    "host": author.host_node.host_url,
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
        Node.external_nodes.create_node("Node a", "http://nodeaaaa.abc/api/")
        response = self.client.post(reverse("user_management:author-list"), data)
        self.assertEqual(response.status_code, 201)
        author = Author.objects.get_by_fqid(data["id"])
        self.assertEqual(author.display_name, data["displayName"])
