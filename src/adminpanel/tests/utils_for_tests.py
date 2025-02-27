from django.contrib.auth.models import User
from django.test import tag

from rest_framework.test import APITestCase

from socialnetwork import models as socialmodels

@tag("US-node-management", "api")
class NodeAdminUserStoryApiTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="admin", password="pass")
        self.user.save()
        self.author = socialmodels.LocalAuthor.objects.create(user=self.user)
        self.author.save()
        self.client.force_authenticate(user=self.user)

        self.sample_authors: list[socialmodels.LocalAuthor] = []
        for i in range(5):
            User.objects.create_user(
                username=f"sample_author_{i}", password="pass")
            sample_author = socialmodels.LocalAuthor.objects.create(
                user=User.objects.get(username=f"sample_author_{i}"))
            self.sample_authors.append(sample_author)
