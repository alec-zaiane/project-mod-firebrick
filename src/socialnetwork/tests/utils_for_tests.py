import json


from django.contrib.auth.models import User
from django.test import tag

from rest_framework.test import APITestCase

from socialnetwork import models as socialmodels
from project_firebrick.settings import THIS_NODE_URL


@tag("api")
class GeneralUserStoryApiTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="user", password="pass")
        self.user.save()
        self.author = socialmodels.LocalAuthor.objects.create(user=self.user)
        self.author.save()
        self.client.force_authenticate(user=self.user)
        self.sample_authors: list[socialmodels.LocalAuthor] = []
        # self.sample_posts[i] is a list of posts made by self.sample_authors[i]
        self.sample_posts: list[list[socialmodels.Post]] = []

    def initialize_sample_authors(self, num_authors: int = 5) -> None:
        """Initialize some sample authors for testing"""
        for i in range(num_authors):
            User.objects.create_user(
                username=f"sample_author_{i}", password="pass")
            sample_author = socialmodels.LocalAuthor.objects.create(
                user=User.objects.get(username=f"sample_author_{i}"),
                github_url="http://github.com",
                display_name=f"Sample Author {i}",)

            self.sample_authors.append(sample_author)

    def initialize_sample_text_posts(self,
                                     posts_per_author: int = 1,
                                     visibility_type: socialmodels.PostTextBased.VisibilityTypes = socialmodels.PostTextBased.VisibilityTypes.PUBLIC,
                                     post_type: socialmodels.PostTextBased.TextPostTypes = socialmodels.PostTextBased.TextPostTypes.PLAINTEXT
                                     ) -> None:
        """Initialize some sample text posts for the sample authors

        Args:
            posts_per_author (int, optional): number of posts each author will "make". Defaults to 1.
            visibility_type (socialmodels.PostTextBased.VisibilityTypes, optional): visibility type of generated posts. Defaults to socialmodels.PostTextBased.VisibilityTypes.PUBLIC.
            post_type (socialmodels.PostTextBased.TextPostTypes, optional): post type of posts. Defaults to socialmodels.PostTextBased.TextPostTypes.PLAINTEXT.
        """
        for user in self.sample_authors:
            this_author_posts: list[socialmodels.Post] = []
            for i in range(posts_per_author):
                post = socialmodels.PostTextBased.objects.create(
                    base_author=user,
                    content=f"sample post {i}",
                    visibility_type=visibility_type,
                    post_type=post_type,
                )
                this_author_posts.append(post)
            self.sample_posts.append(this_author_posts)


class JsonGenerator:
    @staticmethod
    def generate_like(author: socialmodels.Author, target: socialmodels.Post | socialmodels.Comment) -> str:
        like_data = {
            "type": "like",
            "author": {
                "type": "author",
                "id": f"{THIS_NODE_URL}/api/authors/{author.uuid}",
                "host": f"{THIS_NODE_URL}/api/",
                "displayName": author.display_name,
                "github": author.github_url,
                "profileImage": "http://todo.this.needs.to.be.implemented",
                "page": f"{THIS_NODE_URL}/authors/{author.uuid}"
            },
            "published": "2015-03-09T13:07:04+00:00"
        }

        if isinstance(target, socialmodels.Post):
            assert target.author is not None
            like_data["object"] = f"{THIS_NODE_URL}/api/authors/{target.author.uuid}/posts/{target.uuid}"
        elif isinstance(target, socialmodels.Comment):
            raise NotImplementedError("Comments are not implemented yet")
            # TODO like_data["object"] = f"{THIS_NODE_URL}/api/authors/{target.author.uuid}/posts/{target.post.uuid}/comments/{target.uuid}"
        return json.dumps(like_data)
