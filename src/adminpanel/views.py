from typing import Any, List, Dict

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet

from socialnetwork.utils.user_control_decorator import user_control
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from django.contrib.auth.models import User, AnonymousUser
from socialnetwork import models as socialmodels
from socialnetwork import serializers as socialserializers
from .models import AuthorJoinRequest

from .serializers import AuthorJoinRequestSerializer
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def adminpanel_view(request:HttpRequest) -> HttpResponse:
    if isinstance(request.user, AnonymousUser): # can't ever happen, but needed for type checker
        return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))
    requests_active = AuthorJoinRequest.objects.filter(date_denied=None)
    requests_denied = AuthorJoinRequest.objects.exclude(date_denied=None)
    viewer_has_an_author = socialmodels.LocalAuthor.objects.filter(user=request.user).exists()
    viewer_author = socialmodels.LocalAuthor.objects.get(user=request.user) if viewer_has_an_author else None
    return render(request, "adminpanel.html", {
        "viewer_has_an_author": viewer_has_an_author,
        "viewer_author": viewer_author,
        "requests_active": requests_active,
        "requests_denied": requests_denied,
        "current_authors_local": socialmodels.LocalAuthor.objects.all(),
        "current_authors_remote": socialmodels.RemoteAuthor.objects.all(),
    })

@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def hosted_image_view(request:HttpRequest) -> HttpResponse:
    all_hosted_images = socialmodels.HostedImage.objects.all()
    return render(request, "hosted_images.html", {
        "images": all_hosted_images
    })



# API views
@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def author_create_for_superuser(request:Request) -> Response|HttpResponse:
    """Create a LocalAuthor for a superuser, only used in the admin panel for a newly created superuser
    Will serve a redirect if unauthorized
    Expects JSON:
        {
            "user_id": <uuid of authorless superuser>:str
        }
        
    returns JSON if there are errors (code 400):
        {
            "error": <reason>:str
        }
    returns JSON on success (code 201):
        {
            "success": "created":
        }
    """
    superuser_pk = request.data.get("user_id", None)
    if not isinstance(superuser_pk, str):
        return Response({"error": "`user_id` field must be a string"}, status=400)
    if not superuser_pk:
        return Response({"error": "`user_id` field must be non-empty"}, status=400)
    superuser = get_object_or_404(User, pk=superuser_pk)
    if hasattr(superuser, "author"):
        return Response({"error": "Author already exists"}, status=400)
    author = socialmodels.LocalAuthor(user=superuser)
    author.save()
    # return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
    return Response({"success": "created"}, status=201)

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_delete_author(request:Request, author_uuid:str) -> Response:
    """Delete an author
    Will serve a redirect if unauthorized
    
    Expects no body
    returns 404 on failure
    returns JSON on success (code 200)
        {
            "success": "Author deleted"
        }
    """
    author = get_object_or_404(socialmodels.LocalAuthor, uuid=author_uuid)
    author.delete()
    return Response({"success": "Author deleted"}, status=200)
    

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def author_create(request:Request) -> Response|HttpResponse:
    """Create an author directly
    Will serve a redirect if unauthorized
    
    expects JSON
        {
            "username": <username of user>:str
            "password": <password of user>:str
        }
        
    returns JSON on failure (code 400)
        {
            "error": <reason>:str
        }
        
    returns redirect to adminpanel on success
    """
    
    username = request.data.get("username", None)
    password = request.data.get("password", None)
    if not isinstance(username, str) or not isinstance(password, str):
        return Response({"error": "`username` and `password` fields must provided and be strings"}, status=400)
    if not username or not password:
        return Response({"error": "`username` and `password` fields must be non-empty"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)
    # Creating a join request to do this might be overkill, but it keeps the code in one place
    join_request = AuthorJoinRequest.objects.create(username=username, password=password)
    if join_request.get_validity_errors():
        join_request.delete()
        return Response({"error": "Invalid request", "invalid": join_request.get_validity_errors()}, status=400)
    join_request.approve_and_create()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
    # return Response({"success": "User created", "uuid": author.uuid}, status=201)

## Join request API   
@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=True, can_be_superuser=True)
def api_create_join_request(request:Request) -> Response|HttpResponse:
    """Create a join request
    Will serve a redirect if unauthorized
    
    expects JSON 
        {
            "username": <username>:str
            "password": <password>:str
        }
    
    returns JSON on failure (code 400)
        {
            "username": <error about username>:str (optional)
            "password": <error about password>:str (optional)
        }
        
    returns redirect to not_logged_in page on success
    """
    if not hasattr(request, "data"):
        return Response({"error": "Request must have a JSON body"}, status=400)
    data:dict[str,Any] = request.data
    serializer = AuthorJoinRequestSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    serializer.save()
    return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_approve(request:Request, join_request_id:int) -> Response|HttpResponse:
    """Approve a Join Request
    Will serve a redirect if unauthorized
    Expects no body
    returns a 404 when request not found
    returns JSON on error (code 500)
        {
            "error": <reason_for_error>:str
        }
        
    returns a redirect to adminpanel on success
    
    """
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    try:
        join_request.approve_and_create()
    except ValueError as e:
        return Response({"error": str(e)}, status=500)
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_deny(request:Request, join_request_id:int) -> Response|HttpResponse:
    """Deny a Join Request
    Will serve a redirect if unauthorized
    Expects no body
    returns a 404 when request not found
        
    returns a redirect to adminpanel on success
    
    """
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    join_request.deny()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_undeny(request:Request, join_request_id:int) -> Response|HttpResponse:
    """Undeny a Join Request (bring it back into pending state)
    Will serve a redirect if unauthorized
    Expects no body
    returns a 404 when request not found
        
    returns a redirect to adminpanel on success
    
    """
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    join_request.undeny()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["POST"])
@user_control(can_be_author=False, can_be_logged_out=False, can_be_superuser=True)
def api_join_request_delete(request:Request, join_request_id:int) -> Response|HttpResponse:
    """Delete a denied Join Request
    Will serve a redirect if unauthorized
    Expects no body
    returns a 404 when request not found
    
    returns JSON on error (code 400)
        {
            "error": <reason>:string
        }
        
    returns a redirect to adminpanel on success
    
    """
    join_request = get_object_or_404(AuthorJoinRequest, id=join_request_id)
    if not join_request.is_denied:
        return Response({"error": "Only denied requests can be deleted"}, status=400)
    join_request.delete()
    return HttpResponseRedirect(reverse("adminpanel:adminpanel"))

@api_view(["GET", "POST"])
@staff_member_required
def api_hosted_images(request: Request) -> Response:
    """
    GET: Return a list of all hosted images.
        Expects no body
        returns JSON (code 200)
            {
                list of [
                    "id": <image ID>:str
                    "title": <image title>:str
                    "image_url": <URL to fetch to get image file>:str
                    "uploaded_at": <image's upload date>:datetime
                ]
            }
    POST: Upload a new image.
        expects Multipart formData
            "title": title of image:str
            "image": image file:file
            
        returns JSON on success (code 201)
            {
                "detail": "Image uploaded successfully"
                "id": <generated ID of uploaded image>:int
                "title": <title of uploaded image>:str
                "image_url": <url of the image on the server>:str
            }
    """
    if request.method == "POST":
        # Use the DRF serializer to handle file upload & validation
        serializer = socialserializers.HostedImageSerializer(data=request.data)
        if serializer.is_valid():
            hosted_image: socialmodels.HostedImage = serializer.save()
            return Response(
                {
                    "detail": "Image uploaded successfully",
                    "id": hosted_image.pk,
                    "title": hosted_image.title,
                    "image_url": request.build_absolute_uri(hosted_image.image.url),
                },
                status=201,
            )
        return Response(serializer.errors, status=400)

    images: QuerySet[socialmodels.HostedImage] = socialmodels.HostedImage.objects.all().order_by("-uploaded_at")
    data: List[Dict[str, Any]] = []
    for img in images:
        data.append(
            {
                "id": img.pk,
                "title": img.title,
                "image_url": request.build_absolute_uri(img.image.url),
                "uploaded_at": img.uploaded_at.isoformat(),
            }
        )
    return Response(data, status=200)

@api_view(["POST"])
@staff_member_required
def api_delete_hosted_image(request: Request, image_id: int) -> Response:
    """Delete the hosted image
    expects no Body
    returns 404 when image cannot be found
    returns JSON on success (code 204)
        {
            "detail": "Image deleted successfully."
        }
    """
    image = get_object_or_404(socialmodels.HostedImage, pk=image_id)
    if image.image:
        image.image.delete()  
    image.delete()
    return Response({"detail": "Image deleted successfully."}, status=204)

def public_hosted_images(request: HttpRequest) -> HttpResponse:
    """
    A public view listing all hosted images, so regular users can copy their URLs.
    """
    images = socialmodels.HostedImage.objects.all().order_by("-uploaded_at")
    return render(request, "public_hosted_images.html", {"images": images})