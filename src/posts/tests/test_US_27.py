
from django.test import tag
from posts.models import Post, PostTypes, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-visibility", "check-medium")
class TestUserStory27(GeneralUserStoryApiTest):
    """
    Tests for user story 27
    "As an author, posts I create should always be visible to me until they are deleted, so I can find them to edit them or review them or get the link or whatever I want to do with them."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/27
    """

    def test_self_can_see_all_post_types(self) -> None:
        self.initialize_sample_authors(1)
        for _, visibility_type in enumerate(VisibilityTypes):
            self.initialize_sample_text_posts(1, visibility_type=visibility_type)
            post = self.sample_posts[0][-1]
            # make sure we've grabbed the right post
            self.assertEqual(post.author, self.sample_authors[0])
            self.assertEqual(post.visibility_type, visibility_type)

            # check if the author can see the post
            self.assertTrue(post.check_can_be_seen_by(self.sample_authors[0]))
            # these two calls should be identical, but can't hurt to double check
            self.assertTrue(Post.visible_posts.get_posts_visible_to_author(
                self.sample_authors[0]).filter(uuid=post.uuid).exists())

    def test_self_cannot_see_any_deleted_post_types(self) -> None:
        self.initialize_sample_authors(1)
        for _, visibility_type in enumerate(VisibilityTypes):
            self.initialize_sample_text_posts(1, visibility_type=visibility_type)
            post = self.sample_posts[0][-1]
            # make sure we've grabbed the right post
            self.assertEqual(post.author, self.sample_authors[0])
            self.assertEqual(post.visibility_type, visibility_type)

            post.soft_delete()
            # check if the author can see the post
            self.assertFalse(post.check_can_be_seen_by(self.sample_authors[0]))
            # these two calls should be identical, but can't hurt to double check
            self.assertFalse(Post.visible_posts.get_posts_visible_to_author(
                self.sample_authors[0]).filter(uuid=post.uuid).exists())
