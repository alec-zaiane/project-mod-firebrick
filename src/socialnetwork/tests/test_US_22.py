from django.test import tag
from socialnetwork.models import PostTextBased
from .utils_for_tests import GeneralUserStoryApiTest

@tag("US-Visibility")
class TestUserStory22(GeneralUserStoryApiTest):
    """
    Tests for User Story 22
    As an author, I want my friends to see my friends-only, unlisted, and public posts in their stream.
    """

    def setUp(self):
        """Set up test data"""
        # Initialize parent class
        super().setUp()
        
        # Initialize sample_authors list
        self.sample_authors = []
        
        # Create authors
        self.initialize_sample_authors(2)
        self.author1, self.author2 = self.sample_authors[:2]
        
        # Make them friends
        self.author1.following.add(self.author2)
        self.author2.following.add(self.author1)
        
        # Create test posts
        self.public_post = PostTextBased.objects.create(
            base_author=self.author1,
            content="This is a public post",
            visibility_type=PostTextBased.VisibilityTypes.PUBLIC
        )
        
        self.friends_post = PostTextBased.objects.create(
            base_author=self.author1,
            content="This is a friends-only post",
            visibility_type=PostTextBased.VisibilityTypes.FRIENDS_ONLY
        )
        
        self.unlisted_post = PostTextBased.objects.create(
            base_author=self.author1,
            content="This is an unlisted post",
            visibility_type=PostTextBased.VisibilityTypes.UNLISTED
        )

    @tag("check-fast")
    def test_friend_sees_all_posts(self):
        """Test that friends can see all post types in their stream"""
        stream = self.author2.get_stream()
        
        self.assertIn(self.public_post, stream, 
            "Friend should see public posts")
        self.assertIn(self.friends_post, stream, 
            "Friend should see friends-only posts")
        self.assertIn(self.unlisted_post, stream, 
            "Friend should see unlisted posts")

    @tag("check-fast")
    def test_posts_in_correct_order(self):
        """Test that posts appear in reverse chronological order"""
        stream = self.author2.get_stream()
        
        self.assertEqual(stream[0], self.unlisted_post,
            "Most recent post should appear first")
        self.assertEqual(stream[1], self.friends_post,
            "Posts should be in correct order")
        self.assertEqual(stream[2], self.public_post,
            "Oldest post should appear last")