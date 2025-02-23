from typing import Any

from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

# https://stackoverflow.com/questions/53687071/django-rest-framework-not-null-constraint-failed
class PostSerializer(serializers.ModelSerializer[models.Post]):
    author = serializers.PrimaryKeyRelatedField(many=False, queryset=models.Author.objects.all())


class PostTextBasedSerializer(PostSerializer):
    class Meta:
        model = models.PostTextBased
        fields = ["content", "base_author", "visibility_type", "post_type"]

class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

# https://blog.devgenius.io/nested-serializers-in-django-rest-framework-6b36bf011074
class LocalAuthorSerializer(serializers.ModelSerializer[models.LocalAuthor]):
    user = UserSerializer(many=False)
    
    class Meta:
        model = models.LocalAuthor
        fields = ["uuid", "following", "followers", "user", "bio"]
        read_only_fields = ["uuid", "followers"]
        
    def create(self, validated_data:dict[str,Any]) -> Any:
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        author = models.LocalAuthor.objects.create(user=user, **validated_data)
        return author
    
    def update(self, instance:models.LocalAuthor, validated_data:dict[str,Any]) -> Any:
        user_data:Any|None = validated_data.pop("user", [None])[0]
        if user_data is None:
            # should not happen, maybe super can handle it
            return super().update(instance, validated_data)
        user = instance.user
        if isinstance(user_data, dict):
            user.username = user_data.get("username", user.username)
            user.email = user_data.get("email", user.email)
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.save()
        elif isinstance(user_data, str):
            user.username = validated_data.pop("username", [user.username])[0]
            user.email = validated_data.pop("email", [user.email])[0]
            user.first_name = validated_data.pop("first_name", [user.first_name])[0]
            user.last_name = validated_data.pop("last_name", [user.last_name])[0]
            user.save()
        return super().update(instance, validated_data)