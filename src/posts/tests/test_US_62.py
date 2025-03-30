from django.test import tag
from posts.models import Post, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-reading", "check-medium")
class TestUserStory62(GeneralUserStoryApiTest):
    """
    Tests for User Story 62
    "As an author, I want my stream page to show me all the unlisted and friends-only posts of all the authors I follow."
    https://github.com/uofa-cmput404/w25-project-mod-firebrick/issues/62
    """

    def setUp(self) -> None:
        super().setUp()
        # create authors
        self.initialize_sample_authors(3)
        self.viewer = self.sample_authors[0]
        self.followed_friend = self.sample_authors[1]
        self.followed_only = self.sample_authors[2]

        # set up following relationships
        self.viewer.following.add(self.followed_friend)
        self.viewer.following.add(self.followed_only)
        self.followed_friend.following.add(self.viewer)

    @tag("check-fast")
    def test_unlisted_posts_in_stream(self) -> None:
        """
        Test that unlisted posts from followed authors appear in stream
        """
        # create unlisted posts
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.UNLISTED
        )

        # get posts from visible posts manager
        friend_unlisted = Post.visible_posts.filter(
            author=self.followed_friend, visibility_type=VisibilityTypes.UNLISTED
        ).first()
        followed_unlisted = Post.visible_posts.filter(
            author=self.followed_only, visibility_type=VisibilityTypes.UNLISTED
        ).first()

        # get stream posts
        stream_posts = Post.visible_posts.get_posts_in_stream_of_author(
            self.viewer, 0, 10
        )

        # both unlisted posts should be visible
        self.assertIn(friend_unlisted, stream_posts)
        self.assertIn(followed_unlisted, stream_posts)

    @tag("check-fast")
    def test_friends_only_posts_in_stream(self) -> None:
        """
        Test that friends-only posts appear only from mutual followers
        """
        # create friends-only posts
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.FRIENDS_ONLY
        )

        # get posts
        friend_post = Post.visible_posts.filter(
            author=self.followed_friend, visibility_type=VisibilityTypes.FRIENDS_ONLY
        ).first()
        followed_post = Post.visible_posts.filter(
            author=self.followed_only, visibility_type=VisibilityTypes.FRIENDS_ONLY
        ).first()

        # get stream posts
        stream_posts = Post.visible_posts.get_posts_in_stream_of_author(
            self.viewer, 0, 10
        )

        # only mutual follower's post should be visible
        self.assertIn(friend_post, stream_posts)
        self.assertNotIn(followed_post, stream_posts)

    @tag("check-fast")
    def test_all_visibility_types_in_stream(self) -> None:
        """
        Test that stream shows all visibility types from friends
        """
        # create posts with different visibilities
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.PUBLIC
        )
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.UNLISTED
        )
        self.initialize_sample_text_posts(
            posts_per_author=1, visibility_type=VisibilityTypes.FRIENDS_ONLY
        )

        # get friend's posts
        public_post = Post.visible_posts.filter(
            author=self.followed_friend, visibility_type=VisibilityTypes.PUBLIC
        ).first()
        unlisted_post = Post.visible_posts.filter(
            author=self.followed_friend, visibility_type=VisibilityTypes.UNLISTED
        ).first()
        friends_post = Post.visible_posts.filter(
            author=self.followed_friend, visibility_type=VisibilityTypes.FRIENDS_ONLY
        ).first()

        # get stream posts
        stream_posts = Post.visible_posts.get_posts_in_stream_of_author(
            self.viewer, 0, 10
        )

        # all posts should be visible from friend
        self.assertIn(public_post, stream_posts)
        self.assertIn(unlisted_post, stream_posts)
        self.assertIn(friends_post, stream_posts)
