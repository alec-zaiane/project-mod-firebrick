from typing import Any

from rest_framework import serializers

import api.serializers.custom_validators as custom_validators
from api.serializers.author_serializers import AuthorSerializer
from api.serializers.comment_serializers import CommentsSerializer
from api.serializers.like_serializers import LikesSerializer


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
