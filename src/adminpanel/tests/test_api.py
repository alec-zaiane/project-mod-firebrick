from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from adminpanel.models import AuthorJoinRequest
from socialnetwork.models import LocalAuthor

class AdminPanelAPITest(APITestCase):
    def setUp(self) -> None:
        """set up the users and the superusers (admin) including the join request"""

        #normal user
        self.user = User.objects.create_user(username="user", password="pass")

        #superuser (admin)
        self.admin = User.objects.create_user(username="admin", password="pass", is_superuser=True)

        #authenticate as an admin
        self.client.force_authenticate(user=self.admin)

        LocalAuthor.objects.filter(user=self.admin).delete()

        #join request
        self.join_request = AuthorJoinRequest.objects.create(username="new", password="pass")

    def get_join_request_id(self) -> int:
        """Get the most recent ID or raise an error if no requests exist"""
        join_request = AuthorJoinRequest.objects.first()
        #check if its None:
        if join_request is None:
            raise ValueError("No join requests found")  
        return join_request.id 
        
    def test_create_author_for_superuser(self) -> None:
        """test creating an author for a superuser"""

        url = reverse("adminpanel:api_create_author_for_superuser")
        data = {"user_id": str(self.admin.pk)}

        response = self.client.post(url, data, format="json")

        #check if the codes are correct
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #check if url exists, and if redirect still exists
        if hasattr(response, "url"):
            self.assertTrue(response.url.endswith(reverse("adminpanel:adminpanel")))
        else:
            print("Warning: Response object has no `.url` attribute")

        #check if the author was created
        self.assertTrue(LocalAuthor.objects.filter(user=self.admin).exists())

    def test_create_user(self) -> None:
        """test creating a new user"""

        url = reverse("adminpanel:api_create_user")
        data = {"username": "newuser", "password": "password"}

        AuthorJoinRequest.objects.create(username="newuser", password="password")

        response = self.client.post(url, data, format="json")

        #check if the redirect is correct
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #check if the user has been created
        self.assertTrue(User.objects.filter(username="newuser").exists())  

    def test_create_join_request(self) -> None:
        """test submitting a join request"""

        url = reverse("adminpanel:api_create_join_request")
        data = {"username": "join_request", "password": "securepass"}

        response = self.client.post(url, data, format="json")

        #check the redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  

        #check if the request was created
        self.assertTrue(AuthorJoinRequest.objects.filter(username="join_request").exists()) 

    def test_approve_join_request(self) -> None:
        """test approving a join request"""

        join_request_id = self.get_join_request_id()
        url = reverse("adminpanel:api_join_request_approve", args=[join_request_id])

        response = self.client.post(url)

        #check the redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #check if the request was created
        self.assertFalse(AuthorJoinRequest.objects.filter(id=join_request_id).exists())

    def test_deny_join_request(self) -> None:
        """test denying a join request"""

        join_request_id = self.get_join_request_id()
        url = reverse("adminpanel:api_join_request_deny", args=[join_request_id])

        response = self.client.post(url)

        #check the redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #check if the request was created
        self.assertTrue(AuthorJoinRequest.objects.get(id=join_request_id).is_denied)

    def test_undeny_join_request(self) -> None:
        """test undoing a denied join request"""
        
        join_request_id = self.get_join_request_id()
        url = reverse("adminpanel:api_join_request_undeny", args=[join_request_id])

        response = self.client.post(url)

        #check the redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        #check if the request was created
        self.assertFalse(AuthorJoinRequest.objects.get(id=join_request_id).is_denied)

    def test_delete_denied_join_request(self) -> None:
        """test deleting a denied join request"""

        join_request = AuthorJoinRequest.objects.create(username="denied", password="pass")

        #deny request before deleting it
        join_request.deny()

        url = reverse("adminpanel:api_join_request_delete", args=[join_request.id])

        response = self.client.post(url)

        #check the redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        #check if the request was created
        self.assertFalse(AuthorJoinRequest.objects.filter(id=join_request.id).exists())

    