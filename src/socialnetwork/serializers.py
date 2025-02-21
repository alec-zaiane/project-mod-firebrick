from rest_framework import serializers
from . import models

# https://stackoverflow.com/questions/53687071/django-rest-framework-not-null-constraint-failed
class PostSerializer(serializers.ModelSerializer[models.Post]):
    author = serializers.PrimaryKeyRelatedField(many=False, queryset=models.LocalAuthor.objects.all())


class PostTextBasedSerializer(PostSerializer):
    class Meta:
        model = models.PostTextBased
        fields = ["content", "author", "visibility_type", "post_type"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "email", "first_name", "last_name"]

# https://blog.devgenius.io/nested-serializers-in-django-rest-framework-6b36bf011074
class LocalAuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    
    class Meta:
        model = models.LocalAuthor
        fields = ["uuid", "following", "followers"]
        read_only_fields = ["uuid", "followers"]
        
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = models.User.objects.create_user(**user_data)
        author = models.LocalAuthor.create(user=user, **validated_data)
        return author
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        if user_data:
            user = instance.user
            user.username = user_data.get("username", user.username)
            user.email = user_data.get("email", user.email)
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.save()
        return super.update(instance, validated_data)