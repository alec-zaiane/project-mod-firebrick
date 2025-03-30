from django.test import tag
from posts.models import Post, PostTypes, VisibilityTypes
from core.utils.testing_utils import GeneralUserStoryApiTest


@tag("US-visibility")
class TestUserStory25(GeneralUserStoryApiTest):
    """
    Tests for User Story 25
    As an author, I don't want anyone who isn't a friend to be able to
    see my friends-only posts and images.
    """

    def setUp(self) -> None:
        """Set up test data"""
        super().setUp()

        self.sample_authors = []

        # Create authors (2 friends + 1 non-friend)
        self.initialize_sample_authors(3)
        self.author1, self.author2, self.non_friend = self.sample_authors[:3]

        # Make author1 and author2 friends (mutual followers)
        self.author1.following.add(self.author2)
        self.author2.following.add(self.author1)

        # Create friends-only post
        self.friends_post = Post.objects.create_post(
            author=self.author1,
            title="Friends-only post",
            description="This is a friends-only post",
            content="This is a friends-only post",
            post_type=PostTypes.PLAINTEXT,
            visibility_type=VisibilityTypes.FRIENDS_ONLY
        )

    @tag("check-fast")
    def test_non_friend_cannot_see_friends_only_posts(self) -> None:
        """Test that non-friends cannot see friends-only posts in their stream"""
        # Get non-friend's stream
        stream = self.non_friend.get_stream(paginate_start=0, paginate_count=10)

        # Verify friends-only post is not visible
        self.assertNotIn(
            self.friends_post, stream,
            "Non-friend should not see friends-only posts in stream"
        )

    @tag("check-fast")
    def test_non_friend_cannot_access_friends_only_posts(self) -> None:
        """Test that non-friends cannot directly access friends-only posts"""
        # Verify direct access is denied
        self.assertFalse(
            self.friends_post.check_can_be_seen_by(self.non_friend),
            "Non-friend should not be able to access friends-only posts"
        )

    @tag("check-fast")
    def test_friend_can_access_friends_only_posts(self) -> None:
        """Test that friends can access friends-only posts (control test)"""
        # Verify friend can access posts
        self.assertTrue(
            self.friends_post.check_can_be_seen_by(self.author2),
            "Friend should be able to access friends-only posts"
        )
