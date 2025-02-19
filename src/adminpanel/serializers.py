from rest_framework import serializers # type: ignore # missing stub file
from rest_framework import validators # type: ignore # missing stub file
from .models import AuthorJoinRequest
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator

# https://www.geeksforgeeks.org/serializers-django-rest-framework/

class AuthorJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorJoinRequest
        fields = ["username", "password"]
        
    username = serializers.CharField(max_length=150, required=True,
                                     validators = [
                                         validators.UniqueValidator(queryset=AuthorJoinRequest.objects.all(), message="Username has already been requested"),
                                         validators.UniqueValidator(queryset=User.objects.all(), message="Username is already taken"),
                                         UnicodeUsernameValidator(),    
                                     ])