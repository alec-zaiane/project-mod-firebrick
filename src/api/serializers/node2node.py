from __future__ import annotations

from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators


class AuthorSerializer(serializers.Serializer[Any]):
    """Author Serializer for node2node
    Example Author API object from the class docs:
    ```
    {
        // Author object must always have type author
        "type":"author",
        // The full API URL for the author
        "id":"http://nodeaaaa/api/authors/111",
        // The full API URL for the author's node
        "host":"http://nodeaaaa/api/",
        // How the user would like the name to be displayed
        "displayName":"Greg Johnson",
        // URL of the user's github
        "github": "http://github.com/gjohnson",
        // URL of the user's profile image (external image in this example)
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        // URL of the user's HTML profile page
        // It could include an id number/uuid or not
        "page": "http://nodeaaaa/authors/greg"
    }
    ```
    """
    type = serializers.CharField(default="author", validators=[
                                 custom_validators.ExactlyEqualTo("author")])
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField()
    github = serializers.URLField(
        validators=[custom_validators.ContainsValidator("github.com")])
    profileImage = serializers.URLField()
    page = serializers.URLField()


class FollowRequestSerializer(serializers.Serializer[Any]):
    """Follow request serializer for node2node
    Example Follow Request API object from the class docs:
    ```
    {
        "type": "follow",
        "summary":"Greg wants to follow Lara",
        "actor":{
            /* Author object who is sending the request */
        },
        "object":{
            /* Author object who is receiving the request */
        }
    }
    ```
    """
    type = serializers.CharField(default="follow", validators=[
                                 custom_validators.ExactlyEqualTo("follow")])
    summary = serializers.CharField()
    actor = AuthorSerializer()
    object = AuthorSerializer()


class LikeSerializer(serializers.Serializer[Any]):
    """Like Serializer for node2node
    Example Like API object from the class docs:
    ```
    {
        "type":"like",
        "author":{
            /* author object */
        },
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        "id":"http://nodeaaaa/api/authors/111/liked/166",
        // ID of the Comment (UUID)
        "object": "http://nodebbbb/api/authors/222/posts/249"
    }
    ```
    ? how does the like for posts look?
    """
    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("like")])
    author = AuthorSerializer()
    published = serializers.DateTimeField(format='iso-8601')
    id = serializers.URLField()
    object = serializers.URLField()


class LikesSerializer(serializers.Serializer[Any]):
    """Like list serializer for node2node
    Example likes API object from the class docs:
    '''
    {
        "type":"likes",
        // this may or may not be the same as page for the post,
        // depending if there's a seperate URL to just see the comments
        "page":"http://nodeaaaa/authors/222/posts/249"
        "id":"http://nodeaaaa/api/authors/222/posts/249/likes"
        // likes.page, likes.size, likes.count,
        // likes.src should be sent for public and unlisted posts
        // in order to reduce API calls
        // You should return ~ 5 likes per post.
        // should be sorted newest(first) to oldest(last)
        // this is to reduce API call counts
        // number of the first page of likes
        "page_number":1,
        // size of a page of likes
        "size":50,
        // total number of likes
        "count": 9001,
        // the first page of likes
        "src" [
            { /* like object */ }
            { /* like object */ }
        ]
    }
    '''
    """
    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("likes")]
    )
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField(min_value=1)
    size = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    src = serializers.ListField(child=LikeSerializer())


class CommentSerializer(serializers.Serializer[Any]):
    """Comment Serializer for node2node
    Example Comment API object from the class docs:
    ```
    {
        "type":"comment",
        "author": {
            /* author object */
        }
        "comment":"Sick Olde English",
        "contentType":"text/markdown",
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        // ID of the Comment
        "id": "http://nodeaaaa/api/authors/111/commented/130",
        "post": "http://nodebbbb/api/authors/222/posts/249",
        // likes on the comment
        "likes": {
            /* likes object */
        }
    }
    ```
    """
    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("comment")])
    author = AuthorSerializer()
    comment = serializers.CharField()
    contentType = serializers.CharField(validators=[custom_validators.IsInSet({
        "text/markdown", "text/plain"
    })])
    published = serializers.DateTimeField(format='iso-8601')
    id = serializers.URLField()
    post = serializers.URLField()
    likes = LikesSerializer()


class CommentsSerializer(serializers.Serializer[Any]):
    """Comment list serializer for node2node
    Example comments api object from the class docs:
    ```
    {
        "type":"comments",
        // this may or may not be the same as page for the post,
        // depending if there's a seperate URL to just see the comments
        "page":"http://nodebbbb/authors/222/posts/249",
        "id":"http://nodebbbb/api/authors/222/posts/249/comments"
        // comments.page, comments.size, comments.count,
        // comments.src are only sent if:
        // * public
        // * unlisted
        // * friends-only and sending it to a friend
        // You should return ~ 5 comments per post.
        // should be sorted newest(first) to oldest(last)
        // this is to reduce API call counts
        // number of the first page of comments
        "page_number":1,
        // size of comment pages
        "size":5,
        // total number of comments for this post
        "count": 1023,
        // the first page of comments
        "src": [
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ },
            { /* comment object */ }
        ]
    }
    ```
    """
    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("comments")])
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField(min_value=1)
    size = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    src = serializers.ListField(child=CommentSerializer())


class PostSerializer(serializers.Serializer[Any]):
    """Post Serializer for node2node
    Example Post API object from the class docs:
    ```
    {
        "type":"post",
        // title of a post
        "title":"A post title about a post about web dev",
        // id of the post
        // must be the original URL on the node the post came from
        "id":"http://nodebbbb/api/authors/222/posts/249",
        // URL of the user's HTML profile page
        "page": "http://nodebbbb/authors/222/posts/293",
        // a brief description of the post
        "description":"This post discusses stuff -- brief",
        // The content type of the post
        // assume either
        // text/markdown -- common mark
        // text/plain -- UTF-8
        // application/base64 # this an image that is neither a jpeg or png
        // image/png;base64 # this is an png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
        // image/jpeg;base64 # this is an jpeg
        // for HTML you will want to strip tags before displaying
        "contentType":"text/plain",
        "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
        "author": {
            /* author object */
        }
        "comments": {
            /* comments object */
        }
        "likes": {
            /* likes object */
        }
        // ISO 8601 TIMESTAMP
        "published":"2015-03-09T13:07:04+00:00",
        // visibility ["PUBLIC","FRIENDS","UNLISTED","DELETED"]
        "visibility":"PUBLIC"
        // for visibility PUBLIC means it is open to the wild web
        // FRIENDS means if we're friends I can see the post
        // FRIENDS should've already been sent the post so they don't need thi
        // "DELETED" should never show up in the restful API or frontend, but will need to be marked in the database
    }
    ```
    """
    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("post")])
    title = serializers.CharField()
    id = serializers.URLField()
    page = serializers.URLField()
    description = serializers.CharField()
    contentType = serializers.CharField(validators=[custom_validators.IsInSet({
        "text/markdown", "text/plain", "application/base64", "image/png;base64", "image/jpeg;base64"
    })])
    # content = serializers. TODO figure this one out
    author = AuthorSerializer()
    comments = CommentsSerializer()
    likes = LikesSerializer()
    published = serializers.DateTimeField(format='iso-8601')
    visibility = serializers.CharField(validators=[custom_validators.IsInSet({
        "PUBLIC", "FRIENDS", "UNLISTED"
    })])


class PostsSerializer(serializers.Serializer[Any]):
    """Post list serializer for node2node
    Example Posts API object from the class docs:
    ```
    {
        "type":"posts",
        // page number we're on (counting from 1)
        "page_number":23,
        // size of a page of posts
        "size":10,
        // total number of posts
        "count": 9001,
        // the first page of posts
        "src":[
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
            { "type":"post", /* ... the rest of the post object */ },
        ]
    }
    ```
    """

    type = serializers.CharField(
        validators=[custom_validators.ExactlyEqualTo("posts")])
    page_number = serializers.IntegerField(min_value=1)
    size = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    src = serializers.ListField(child=PostSerializer())
