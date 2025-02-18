from rest_framework import serializers # type: ignore # missing stub file
from .models import AuthorJoinRequest

# https://www.geeksforgeeks.org/serializers-django-rest-framework/

class AuthorJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorJoinRequest
        fields = ["username", "password"]