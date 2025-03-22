from django.test import TestCase

from posts.tests import dummies
from user_management.tests import dummies as user_dummies
from posts.forms import CreatePostForm
from posts.models import Post, PostTypes, VisibilityTypes

"""Unit Tests for User Management forms"""


class CreatePostFormUnitTests(TestCase):
    def test_create_post_form_valid(self) -> None:
        """Test that the form is valid with valid data"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())

    def test_create_post_form_no_title(self) -> None:
        """Test that the form is invalid with no title"""
        form = CreatePostForm(data={
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["title"], ["Please provide a title."])

    def test_create_post_form_no_content(self) -> None:
        """Test that the form is invalid with no content"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["content"], ["Please provide content."])

    def test_create_post_form_no_post_type(self) -> None:
        """Test that the form is invalid with no post type"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["post_type"], ["Please choose a post type."])

    def test_create_post_form_no_visibility_type(self) -> None:
        """Test that the form is invalid with no visibility type"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["visibility_type"], ["Please choose a visibility type."])

    def test_create_minimal(self) -> None:
        """Test that the form is valid with minimal data"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())

    def test_create_post_form_invalid_post_type(self) -> None:
        """Test that the form is invalid with an invalid post type"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": "invalid",
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["post_type"], [
                         "Select a valid choice. invalid is not one of the available choices."])

    def test_create_post_form_invalid_visibility_type(self) -> None:
        """Test that the form is invalid with an invalid visibility type"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": "invalid",
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["visibility_type"], [
                         "Select a valid choice. invalid is not one of the available choices."])
