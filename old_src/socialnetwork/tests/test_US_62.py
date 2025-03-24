from django.test import tag
from socialnetwork.models import PostTextBased
from .utils_for_tests import GeneralUserStoryApiTest

@tag("US-Visibility")
class TestUserStory62(GeneralUserStoryApiTest):
    """
    Tests for User Story 62
    "As an author, I want my stream page to show me all the unlisted and 
    friends-only posts of all the authors I follow."
    """

    def setUp(self) -> None:
        """Set up test data"""
        super().setUp()
        
        self.sample_authors = []
        
        # Create authors (viewer and 2 authors to follow)
        self.initialize_sample_authors(3)
        self.viewer, self.author1, self.author2 = self.sample_authors[:3]
        
        # Make viewer follow both authors
        self.viewer.following.add(self.author1)
        self.viewer.following.add(self.author2)
        
        # Make viewer friends with author1 but just following author2
        self.author1.following.add(self.viewer)  # mutual following = friends
        
        # Create test posts for author1 (friend)
        self.friend_unlisted = PostTextBased.objects.create(
            base_author=self.author1,
            content="Friend's unlisted post",
            visibility_type=PostTextBased.VisibilityTypes.UNLISTED
        )
        
        self.friend_friends_only = PostTextBased.objects.create(
            base_author=self.author1,
            content="Friend's friends-only post",
            visibility_type=PostTextBased.VisibilityTypes.FRIENDS_ONLY
        )
        
        # Create test posts for author2 (following but not friend)
        self.following_unlisted = PostTextBased.objects.create(
            base_author=self.author2,
            content="Following author's unlisted post",
            visibility_type=PostTextBased.VisibilityTypes.UNLISTED
        )
        
        self.following_friends_only = PostTextBased.objects.create(
            base_author=self.author2,
            content="Following author's friends-only post",
            visibility_type=PostTextBased.VisibilityTypes.FRIENDS_ONLY
        )

    @tag("check-fast")
    def test_stream_shows_followed_authors_unlisted_posts(self) -> None:
        """Test that stream shows unlisted posts from followed authors"""
        stream = self.viewer.get_stream()
        
        self.assertIn(
            self.friend_unlisted, stream,
            "Stream should show unlisted posts from friends"
        )
        self.assertIn(
            self.following_unlisted, stream,
            "Stream should show unlisted posts from followed authors"
        )

    @tag("check-fast")
    def test_stream_shows_friends_only_posts_from_friends(self) -> None:
        """Test that stream shows friends-only posts only from friends"""
        stream = self.viewer.get_stream()
        
        self.assertIn(
            self.friend_friends_only, stream,
            "Stream should show friends-only posts from friends"
        )
        self.assertNotIn(
            self.following_friends_only, stream,
            "Stream should NOT show friends-only posts from non-friend followed authors"
        )
        
    @tag("check-fast")
    def test_stream_shows_correct_number_of_posts(self) -> None:
        """Test that stream shows the expected number of posts"""
        stream = self.viewer.get_stream()
        # Should see a total of 3 posts (2 unlisted + 1 friends-only)
        self.assertEqual(
            len(stream), 3,
            "Stream should show exactly 3 posts (2 unlisted + 1 friends-only)"
        )