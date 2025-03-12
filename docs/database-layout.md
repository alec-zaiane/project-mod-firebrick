# The new Backend
Structure is separated into multiple distinct apps: `comments`, `likes`, `posts`, and `user_management`. `core` is the "project" folder that contains stuff like `settings.py`

## Important:
Instead of `<Model>.objects.(...)` or similar, many of the models have extra `Manager`s that can return the set of what you're looking for (eg: `Authors.local_authors.(...)`), these will be outlined below, and are always better to use if you can (they give better type hints)

In addition, most `Model.objects` Managers will have a `create_xyz()` function that makes it easier to create an xyz (they have proper arguments). *Always use these instead of `create()` if available*

## Double important:
***Never* use `<Model>.objects.(...)` inside a view, with the exception of `.all()` and `.create_<thing>()`**.

 I.e: if you need to `.filter()` or anything else like that, find a way to put it in a `models.py`, or talk to me about it and we can find the best place to put it (often it'll be in a `Manager`)

## The Admin Panel
`/admin` is actually useful this time, and we will no longer have our `/adminpanel` endpoint
- you can approve/deny join requests
- you can soft delete posts
- more functionality will be added as needed
- creating API objects directly is janky for now, just put `127.0.0.1:8000/<some_gibberish>` in the FQID if you are manually making Posts/Likes/Comments
    - change the gibberish everytime or else you may run into uniqueness constraint errors
- *Do not manually create authors unless they are external*

## `core` folder
- (this is like our old `project_firebrick` folder)
- has `settings.py` etc
- contains `utils` folder with some project-wide utils
    - `adminpanel.py` has `/admin` related helper functions, `testing_utils.py` has testing related helpers
    - this folder contains the `ApiObject` abstract model, which all external Api-related models extend (`Author`, `Post`, `Comment`, `Like`)
    - The `ApiObject` model has extra fields that are easy to forget about when looking at each individual model:
        - `uuid`: a UUID
        - `host_node`: the `Node` object representing which node hosts this object (see `user_management`)
        - `fqid`: the FQID of this object (any subclasses of `ApiObject` must implement a `generate_fqid(self)` function to supply the value)
        - `created_at`: datetime of when the object was created
        - `updated_at`: datetime of when the object was last updated/edited
        - `is_updated` (property): true if the object has ever been updated


## `user_management` app
- For user management related models/views/api views
- `User`: extension of Django's built-in user class, you won't need to touch this one
- `Author(ApiObject)`: a representation of an author, (either local or external)
    - **To create a local author, use joinRequests**
    - local authors have a `user` set, external authors will have `user==None`
        - when using `Author.local_authors.(...)` and `Author.external_authors.(...)` the typing system will know this inherently!
    - has extra managers:
        - `Author.local_authors`: only authors local to this node
        - `Author.external_authors`: only authors not local to this node
- `LocalAuthor` and `ExternalAuthor` are proxy models for `Author` (ie: they don't exist in the database, but provide nicer typing for you to use in other parts of the codebase)
- `Node`: an instance of an API-compatible system to ours
    - `Node.objects.get_local_node()` will return (or create) a singleton Node representing the "self" server (the server that is running the code)
- `JoinRequest`: a request to join the node as an author
    - you can create it, then `.approve()` it to create the linked `Author` and `User` required for a local author

## `posts` app
- `PostTypes`: enum for types of post, *we no longer have `PostTextBased` and `PostMediaBased`, just `Post`*
- `VisibilityTypes`: enum for visibility types
- `Post`: represents any type of post, the type is dictated by a `post_type` value
    - *use `Post.objects.create_post()` to create a post!*
    - use `soft_delete()` to "delete" it (**Changed from our current scheme!**)
    - has a `p.likes` and `p.comments` that return `QuerySet`s of `Like` and `Comment` objects targeting them, respectively
    - has extra managers:
        - `objects`: the base manager has been customized with additional properties:
            - `Post.objects.plaintext`: all plaintext posts
            - `Post.objects.markdown`: all markdown posts
            - `Post.objects.image`: all image posts
            - `Post.objects.video`: all iamge posts
        - `deleted_posts`: all deleted posts
            - includes all `.plaintext`, `.markdown`, etc properties as well
        - `visible_posts`: all visible (non-deleted) posts
            - includes all `.plaintext`, `.markdown`, etc properties as well

## `comments` app
- `Comment`: a comment on a post
    - *use `Comment.objects.create_comment()` to create one!*
    - has a `likes` field returning a `Queryset` of `Like` objects targeting it

## `likes` app
- `Like`: a like by an `Author` on either a `Post` or a `Comment`
    - *use `Like.objects.create_like()` to create one!*
    - has extra managers:
        - `Like.post_likes`: all likes on posts
        - `Like.comment_likes`: all likes on comments
    - if you have used one of the extra managers to retrieve a `Like`, you can use `retrieved_like.target` to find the `Comment` or `Post` that the like is targeting, the type system will help you here too!
