from django.test import TestCase, tag
from django.db.models import QuerySet

"""This file is for general tests that don't match any specific user story"""


from user_management.models import Node
from user_management.tests.dummies import create_dummy_local_author
from posts.models import Post, PostTypes, VisibilityTypes
from posts.tests.dummies import create_dummy_post


@tag("check-medium")
class PostUnitTests(TestCase):
    def setUp(self) -> None:
        self.local_node = Node.objects.get_local_node()
        self.author = create_dummy_local_author("test_user", "a@a.com")

    def test_post_types_creation_deletion(self) -> None:
        post_plain = create_dummy_post(self.local_node, self.author, post_type=PostTypes.PLAINTEXT)
        post_markdown = create_dummy_post(
            self.local_node, self.author, post_type=PostTypes.MARKDOWN)
        post_image = create_dummy_post(self.local_node, self.author, post_type=PostTypes.IMAGE)
        post_video = create_dummy_post(self.local_node, self.author, post_type=PostTypes.VIDEO)

        # just to make the rest more readable
        def get_typed_posts(type: PostTypes) -> QuerySet[Post]:
            return Post.visible_posts.get_typed_posts(type)

        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.visible_posts.count(), 4)
        self.assertEqual(get_typed_posts(PostTypes.PLAINTEXT).count(), 1)
        self.assertEqual(get_typed_posts(PostTypes.MARKDOWN).count(), 1)
        self.assertEqual(get_typed_posts(PostTypes.IMAGE).count(), 1)
        self.assertEqual(get_typed_posts(PostTypes.VIDEO).count(), 1)

        post_plain.soft_delete()
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.visible_posts.count(), 3)
        self.assertEqual(Post.deleted_posts.count(), 1)
        self.assertEqual(get_typed_posts(PostTypes.PLAINTEXT).count(), 0)

        post_markdown.soft_delete()
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.visible_posts.count(), 2)
        self.assertEqual(Post.deleted_posts.count(), 2)
        self.assertEqual(get_typed_posts(PostTypes.MARKDOWN).count(), 0)

        post_image.soft_delete()
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.visible_posts.count(), 1)
        self.assertEqual(Post.deleted_posts.count(), 3)
        self.assertEqual(get_typed_posts(PostTypes.IMAGE).count(), 0)

        post_video.soft_delete()
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(Post.visible_posts.count(), 0)
        self.assertEqual(Post.deleted_posts.count(), 4)
        self.assertEqual(get_typed_posts(PostTypes.VIDEO).count(), 0)
