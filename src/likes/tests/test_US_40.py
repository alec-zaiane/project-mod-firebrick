
from django.test import tag
from django.urls import reverse


from core.utils.testing_utils import UITestCase

from posts.models import PostTypes
from comments.models import Comment
from likes.models import Like


@tag("US-comments/likes")
class TestUserStory40UI(UITestCase):
    """
    Test for User Story 40:
    As an author, I want to like comments that I can access, so I can show my appreciation.
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/40
    """
    def test_can_like_post_comment(self) -> None:
        self.initialize_sample_authors(2)
        self.initialize_sample_text_posts(posts_per_author=1)
        comment = Comment.objects.create_comment(self.sample_authors[0], self.sample_posts[1][0], "My cool comment", PostTypes.PLAINTEXT)

        # try to like a comment
        self.login_as(self.sample_authors[1])
        self.visit(reverse("posts:view_post", args=[self.sample_posts[1][0].uuid]))
        comment_card = self.find_element_by_id(f"comment-{comment.uuid}")
        comment_card.find_element_by_selector("button.like-button").click()

        # make sure the like exists
        self.assertEqual(Like.objects.count(), 1)
        like = Like.objects.first()
        assert like is not None # for mypy
        self.assertEqual(like.target, comment)
        self.assertEqual(like.author, self.sample_authors[1])

        # now unlike it
        comment_card = self.find_element_by_id(f"comment-{comment.uuid}")
        comment_card.find_element_by_selector("button.like-button").click()

        # make sure the like is gone
        self.assertEqual(Like.objects.count(), 0)
        self.end_test()

