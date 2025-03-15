from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from posts.models import Post, PostTypes, VisibilityTypes
# used request.user.author instead of the user_control for LocalAuth we had set up before it seems like 
# it could be better cuz there's built in authenticator, gonna look at this tonight to see
from user_management.models import LocalAuthor 


@api_view(["POST"])
def api_textpost_create(request):
    """Create a new plaintext or markdown post."""
    viewer = request.user.author
    data = request.data.copy()

    # Default to plaintext
    post_type = data.get("post_type", PostTypes.PLAINTEXT)  
    visibility_type = data.get("visibility_type", VisibilityTypes.PUBLIC)

    if post_type not in PostTypes.values:
        return Response({"error": "Invalid post type"}, status=400)

    post = Post.objects.create_post(
        author=viewer,
        title=data.get("title", "Untitled Post"),
        description=data.get("description", ""),
        content=data.get("content", ""),
        post_type=post_type,
        visibility_type=visibility_type
    )

    return Response({"detail": "Post created", "post_id": post.uuid}, status=201)


@api_view(["POST"])
def api_textpost_update(request, post_uuid: str):
    """Modify a post"""
    post = get_object_or_404(Post, uuid=post_uuid)
    viewer = request.user.author

    if post.author != viewer:
        return Response({"error": "You must be the author to modify this post"}, status=403)

    post.edit(
        new_content=request.data.get("content", post.content),
        new_type=request.data.get("post_type", post.post_type)
    )

    return Response({"detail": "Post updated", "post_id": post.uuid}, status=200)

@api_view(["POST"])
def api_imagepost_create(request):
    """Create an image post and return the Markdown image link."""
    # user must be autheicated 
    viewer = request.user.author  

    if "image" not in request.FILES:
        return Response({"error": "No image file provided"}, status=400)

    image_file = request.FILES["image"]

    # Creating the post with the uploaded image
    post = Post.objects.create_post(
        author=viewer,
        title=request.data.get("title", "Image Post"),
        description=request.data.get("description", ""),
        # Storing the image in the content field
        content=image_file,  
        post_type=PostTypes.IMAGE,  
        visibility_type=request.data.get("visibility_type", VisibilityTypes.PUBLIC)
    )

    # Generating a Markdown link for the uploaded image
    markdown_url = f"![{image_file.name}]({post.content.url})"

    return Response({
        "detail": "Image post created",
        "post_id": post.uuid,
        "markdown": markdown_url  
    }, status=201)

