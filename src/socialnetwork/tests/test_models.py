from django.test import TestCase
from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, PostTextBased, Post

class AuthorPostVisibilityTest(TestCase):
    def setUp(self) -> None:
        """
        this will set up an author and will also create a post wity different visibility settings
        """
        self.user = User.objects.create(username="404")
        self.author = LocalAuthor.objects.create(user = self.user)

        #create a unlistet post
        self.unlisted_post = PostTextBased.objects.create(base_author = self.author, 
                                                          content = "testing unlisted post", 
                                                          visibility_type = Post.VisibilityTypes.UNLISTED
                                                          )

        #create a friends-only post
        self.friends_only_post = PostTextBased.objects.create(base_author = self.author, 
                                                              content = "testing friends_only post", 
                                                              visibility_type = Post.VisibilityTypes.FRIENDS_ONLY
                                                              )

        #create a public post
        self.public_post = PostTextBased.objects.create(base_author = self.author, 
                                                        content = "testing public post", 
                                                        visibility_type = Post.VisibilityTypes.PUBLIC
                                                        )
        
        self.public_post.send_to_required_private_inboxes()
        self.unlisted_post.send_to_required_private_inboxes()
        self.friends_only_post.send_to_required_private_inboxes()

    def test_author_can_see_own_post(self) -> None:
        """
        test to see if the author can see all types of their own post
        """
        #assertions to check
        self.assertTrue(self.public_post._check_can_be_seen_by(self.author))
        self.assertTrue(self.unlisted_post._check_can_be_seen_by(self.author))
        self.assertTrue(self.friends_only_post._check_can_be_seen_by(self.author))

    def test_author_cannot_see_deleted_post(self) -> None:
        """
        test to see if an author can see deleted posts or not
        """
        #remove the posts
        self.public_post.delete()
        self.unlisted_post.delete()
        self.friends_only_post.delete()
        
        #refresh the database before checking in case delete() does not refresh
        with self.assertRaises(PostTextBased.DoesNotExist):
            self.public_post.refresh_from_db()  
        with self.assertRaises(PostTextBased.DoesNotExist):
            self.unlisted_post.refresh_from_db()
        with self.assertRaises(PostTextBased.DoesNotExist):
            self.friends_only_post.refresh_from_db()

        #assertions to check
        self.assertTrue(self.public_post._check_can_be_seen_by(self.author))
        self.assertTrue(self.unlisted_post._check_can_be_seen_by(self.author))
        self.assertTrue(self.friends_only_post._check_can_be_seen_by(self.author))
        
