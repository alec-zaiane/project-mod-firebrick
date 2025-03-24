import shutil
import tempfile
from posts.models import Post, PostTypes, VisibilityTypes
from posts.forms import CreatePostForm
from user_management.tests import dummies as user_dummies
from posts.tests import dummies
from django.test import TestCase, override_settings


"""Unit Tests for User Management forms"""


class CreatePostFormUnitTests(TestCase):
    def setUp(self) -> None:
        """Sets up a temporary directory, and makes some images for later use in tests"""
        super().setUp()

        self.temp_media_root = tempfile.mkdtemp()
        self.override_settings = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.override_settings.enable()
        self.image = dummies.create_dummy_post_image()
        self.invalid_image = dummies.create_dummy_invalid_post_image()

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

    def test_create_valid_image_post(self) -> None:
        """Tests that the form can create a valid image post"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "post_type": PostTypes.IMAGE,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())
        self.assertTrue(Post.objects.get(title="Test Title").image)

    def test_minimum_image_post(self) -> None:
        """Tests that an image post can be made with the minimum required fields"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "post_type": PostTypes.IMAGE,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())
        self.assertTrue(Post.objects.get(title="Test Title").image)

    def test_invalid_image_post(self) -> None:
        """Tests that the form is invalid with an invalid image"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "post_type": PostTypes.IMAGE,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.invalid_image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["image"], [
                         "Upload a valid image. The file you uploaded was either not an image or a corrupted image."])

    def test_no_image_post(self) -> None:
        """Tests that the form is invalid with no image"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "post_type": PostTypes.IMAGE,
            "visibility_type": VisibilityTypes.PUBLIC,
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["image"], ["This field is required."])

    def test_content_removed_from_image_post(self) -> None:
        """Tests that a valid image post will remove appended content"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.IMAGE,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())
        self.assertFalse(Post.objects.get(title="Test Title").content)

    def test_image_removed_from_plaintext_post(self) -> None:
        """Tests that a valid plaintext post will remove appended image"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())
        self.assertFalse(Post.objects.get(title="Test Title").image)

    def test_image_removed_from_markdown_post(self) -> None:
        """Tests that a valid markdown post will remove appended image"""
        form = CreatePostForm(data={
            "title": "Test Title",
            "description": "Test Description",
            "content": "Test Content",
            "post_type": PostTypes.MARKDOWN,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, files={
            "image": self.image
        })
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Test Title").exists())
        self.assertFalse(Post.objects.get(title="Test Title").image)

    def test_modify_post(self) -> None:
        """Tests that a post can be modified"""
        author = user_dummies.create_dummy_local_author("test_author", "abc@a.com")
        post = dummies.create_dummy_post(author=author, host_node=author.host_node, title="Test Title",
                                         description="Test Description", content="Test Content")
        form = CreatePostForm(data={
            "title": "Modified Title",
            "description": "Modified Description",
            "content": "Modified Content",
            "post_type": PostTypes.PLAINTEXT,
            "visibility_type": VisibilityTypes.PUBLIC,
        }, instance=post)
        form.instance.author = author
        form.instance.host_node = author.host_node
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Post.objects.filter(title="Modified Title").exists())
        self.assertFalse(Post.objects.filter(title="Test Title").exists())

    def tearDown(self) -> None:
        """Disables the temporary override settings that were made for these tests"""
        self.override_settings.disable()
        shutil.rmtree(self.temp_media_root)
        super().tearDown()
