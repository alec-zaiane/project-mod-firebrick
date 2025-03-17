from rest_framework import routers
from django.urls import URLPattern, URLResolver

from user_management.viewsets import AuthorViewSet

app_name = "user_management"
urlpatterns: list[URLPattern | URLResolver] = [

]

router = routers.SimpleRouter()
# creates names: author-list, author-detail, author-create, author-update, author-delete
router.register(r"api/authors", AuthorViewSet)

urlpatterns += router.urls
