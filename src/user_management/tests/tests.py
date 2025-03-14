from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from user_management.tests import dummies
from user_management.models import Author, JoinRequest


"""General tests that don't match any specific user story"""


class JoinRequestUnitTests(TestCase):
    def test_join_request_approval(self) -> None:
        # make a join request and approve it
        join_request = dummies.create_dummy_join_request("test_user", "abc@a.com")
        author = join_request.approve()

        # make sure the author was created properly
        self.assertEqual(author.username, "test_user")
        self.assertEqual(author.user.email, "abc@a.com")
        self.assertIn(author, Author.objects.all())
        self.assertIn(author, Author.local_authors.all())
        self.assertNotIn(author, Author.external_authors.all())

        # make sure the join request was deleted
        self.assertNotIn(join_request, JoinRequest.objects.all())
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_join_request_deny(self) -> None:
        # make a join request and deny it
        join_request = dummies.create_dummy_join_request("test_user", "abc@a.com")
        join_request.deny()

        # make sure no author was created
        self.assertEqual(Author.objects.count(), 0)

        # make sure the join request still exists
        self.assertIn(join_request, JoinRequest.objects.all())
        self.assertEqual(JoinRequest.objects.count(), 1)

        # now delete it
        join_request.delete()
        self.assertEqual(JoinRequest.objects.count(), 0)

    def test_join_request_deny_undeny(self) -> None:
        # make a join request and deny it
        join_request = dummies.create_dummy_join_request("test_user", "abc@a.com")
        join_request.deny()
        join_request.undeny()
        author = join_request.approve()

        self.assertEqual(author.username, "test_user")
        self.assertEqual(author.user.email, "abc@a.com")

    def test_multiple_join_requests_possible(self) -> None:
        join_request_a = dummies.create_dummy_join_request("test_user", "abc@a.com")
        join_request_b = dummies.create_dummy_join_request("another_user", "def@g.com")
        join_request_c = dummies.create_dummy_join_request("yet_another_user", "ghi@j.com")

        self.assertEqual(JoinRequest.objects.count(), 3)
        self.assertEqual(Author.objects.count(), 0)

        author_a = join_request_a.approve()
        author_b = join_request_b.approve()
        author_c = join_request_c.approve()

        self.assertEqual(JoinRequest.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 3)
        self.assertIn(author_a, Author.objects.all())
        self.assertIn(author_b, Author.objects.all())
        self.assertIn(author_c, Author.objects.all())

    def test_join_request_fail_on_clashing_usernames(self) -> None:
        join_request_a = dummies.create_dummy_join_request("test_user", "abc@a.com")
        with self.assertRaises(IntegrityError):
            join_request_b = dummies.create_dummy_join_request("test_user", "def@g.com")

    def test_join_request_fail_on_clashing_emails(self) -> None:
        join_request_a = dummies.create_dummy_join_request("test_user", "abc@a.com")
        with self.assertRaises(IntegrityError):
            join_request_b = dummies.create_dummy_join_request("another_user", "abc@a.com")

    def test_join_request_fail_when_username_exists_in_users(self) -> None:
        join_request_a = dummies.create_dummy_join_request("test_user", "abc@a.com")
        author = join_request_a.approve()
        with self.assertRaises(ValidationError):
            join_request_b = dummies.create_dummy_join_request("test_user", "def@g.com")

    def test_join_request_fail_when_email_exists_in_users(self) -> None:
        join_request_a = dummies.create_dummy_join_request("test_user", "abc@a.com")
        author = join_request_a.approve()
        with self.assertRaises(ValidationError):
            join_request_b = dummies.create_dummy_join_request("another_user", "abc@a.com")
