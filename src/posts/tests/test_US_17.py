from django.test import tag
from posts.models import Post, VisibilityTypes, PostTypes
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-reading", "check-medium")
class TestUserStory17(GeneralUserStoryApiTest):
    """
    Tests for User Story 17
    "As an author, I want a stream which shows all the posts I should know about"
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/17
    """

    def setUp(self) -> None:
        super().setUp()
        self.viewer = self.author

        # create other authors
        self.initialize_sample_authors(2)
        self.followed_author = self.sample_authors[0]
        self.unfollowed_author = self.sample_authors[1]

        # set up following relationship
        self.viewer.following.add(self.followed_author)

    @tag("check-fast")
    def test_stream_shows_followed_author_unlisted_posts(self) -> None:
        """
        Test that stream shows unlisted posts from followed authors
        """
        # create unlisted post for followed author
        followed_post = Post.objects.create_post(
            author=self.followed_author,
            title="Followed unlisted post",
            description="This is a followed unlisted post",
            content="Followed unlisted content",
            post_type=PostTypes.PLAINTEXT,
            visibility_type=VisibilityTypes.UNLISTED,
        )

        # get stream posts
        stream_posts = list(
            Post.visible_posts.get_posts_in_stream_of_author(
                self.viewer, paginate_start=0, paginate_count=10
            )
        )

        # verify followed author's unlisted post is visible
        self.assertIn(
            followed_post,
            stream_posts,
            "Followed author's unlisted post should be visible",
        )

    @tag("check-fast")
    def test_stream_does_not_show_unfollowed_unlisted_posts(self) -> None:
        """
        Test that stream doesn't show unlisted posts from unfollowed authors
        """
        # create unlisted post for unfollowed author
        unfollowed_post = Post.objects.create_post(
            author=self.unfollowed_author,
            title="Unfollowed unlisted post",
            description="This is an unfollowed unlisted post",
            content="Unfollowed unlisted content",
            post_type=PostTypes.PLAINTEXT,
            visibility_type=VisibilityTypes.UNLISTED,
        )

        # get stream posts
        stream_posts = list(
            Post.visible_posts.get_posts_in_stream_of_author(
                self.viewer, paginate_start=0, paginate_count=10
            )
        )

        # verify unfollowed author's unlisted post is not visible
        self.assertNotIn(
            unfollowed_post,
            stream_posts,
            "Unfollowed author's unlisted post should not be visible",
        )

    @tag("check-fast")
    def test_stream_shows_own_unlisted_posts(self) -> None:
        """
        Test that stream shows author's own unlisted posts
        """
        # create own unlisted post
        own_post = Post.objects.create_post(
            author=self.viewer,
            title="Own unlisted post",
            description="This is my own unlisted post",
            content="Own unlisted content",
            post_type=PostTypes.PLAINTEXT,
            visibility_type=VisibilityTypes.UNLISTED,
        )

        stream_posts = list(
            Post.visible_posts.get_posts_in_stream_of_author(
                self.viewer, paginate_start=0, paginate_count=10
            )
        )

        # verify own unlisted post is visible
        self.assertIn(own_post, stream_posts, "Own unlisted post should be visible")
