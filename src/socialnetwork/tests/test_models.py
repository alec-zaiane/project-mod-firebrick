from django.test import TestCase
from django.contrib.auth.models import User
from socialnetwork.models import LocalAuthor, PostPlainText, Post

class AuthorPostVisibilityTest(TestCase):
    def setUp(self):
        """
        this will set up an author and will also create a post wity different visibility settings
        """
        self.user = User.objects.create(username="404")
        self.author = LocalAuthor.objects.create(user = self.user)

        #create a unlistet post
        self.unlisted_post = PostPlainText.objects.create(author = self.author, 
                                                          content = "testing unlisted post", 
                                                          visibility_type = Post.VisibilityTypes.UNLISTED
                                                          )

        #create a friends-only post
        self.friends_only_post = PostPlainText.objects.create(author = self.author, 
                                                              content = "testing friends_only post", 
                                                              visibility_type = Post.VisibilityTypes.FRIENDS_ONLY
                                                              )

        #create a public post
        self.public_post = PostPlainText.objects.create(author = self.author, 
                                                        content = "testing public post", 
                                                        visibility_type = Post.VisibilityTypes.PUBLIC
                                                        )

    def test_author_can_see_own_post(self):
        """
        test to see if the author can see all types of their own post
        """
        posts = PostPlainText.objects.filter(author = self.author)  #creates a post

        #assertions to check
        self.assertIn(self.public_post, posts)  
        self.assertIn(self.unlisted_post, posts)
        self.assertIn(self.friends_only_post, posts)

    def test_author_cannot_see_deleted_post(self):
        """
        test to see if an author can see deleted posts or not
        """
        #remove the posts
        self.public_post.delete()
        self.unlisted_post.delete()
        self.friends_only_post.delete()
        
        #create a post, but should not be within the authors' post
        posts = PostPlainText.objects.filter(author=self.author)
        self.assertNotIn(self.public_post, posts)
        self.assertNotIn(self.unlisted_post, posts)
        self.assertNotIn(self.friends_only_post, posts)
