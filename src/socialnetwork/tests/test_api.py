"""this file will handle all the testing for API's created"""

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from socialnetwork.models import LocalAuthor, PostTextBased


class APICreatePOstTest(APITestCase):
    def setUp(self) -> None:
        """this wil set up a user and the author for testing"""
        self.user = User.objects.create_user(username="user", password="pass")
        self.author = LocalAuthor.objects.create(user=self.user)

        # user can be authenticated
        self.client.force_authenticate(user=self.user)

        # the path name
        self.post_url = reverse("socialnetwork:api_create_text_post")

    def test_create_post(self) -> None:
        """create a post test"""

        info = {"content": "test post",
                "post_type": "PT",
                "visibility_type": "PU"}

        response = self.client.post(self.post_url, info, format="json")

        # to check if its been created (the post)
        self.assertEqual(response.status_code, 201)
        # to check if its in the DB
        self.assertEqual(PostTextBased.objects.count(), 1)

    def test_delete_post(self) -> None:

        post = PostTextBased.objects.create(
            content="Test post",
            post_type=PostTextBased.TextPostTypes.PLAINTEXT,
            base_author=self.author,
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC
        )

        self.assertEqual(
            len(PostTextBased.objects.filter(base_author=self.author)),
            1
        )

        """delete a post test"""
        self.client.post(
            reverse("socialnetwork:api_post_delete", args=[post.uuid]),
        )

        self.assertTrue(
            PostTextBased.objects.filter(
                base_author=self.author).get().is_deleted
        )
