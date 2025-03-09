from typing import Any

from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

# https://stackoverflow.com/questions/53687071/django-rest-framework-not-null-constraint-failed


class PostSerializer(serializers.ModelSerializer[models.Post]):
    author = serializers.PrimaryKeyRelatedField(
        many=False, queryset=models.Author.objects.all())


class PostTextBasedSerializer(PostSerializer):
    class Meta:
        model = models.PostTextBased
        fields = ["content", "base_author", "visibility_type", "post_type"]
        read_only_fields = ["base_author"]


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

# https://blog.devgenius.io/nested-serializers-in-django-rest-framework-6b36bf011074


class LocalAuthorSerializer(serializers.ModelSerializer[models.LocalAuthor]):
    user = UserSerializer(many=False)

    class Meta:
        model = models.LocalAuthor
        fields = ["uuid", "following", "followers", "bio", "user"]
        read_only_fields = ["uuid", "followers"]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        validated_data: dict[str, Any] = super().validate(data)
        if "username" in validated_data:
            if User.objects.filter(username=validated_data["username"]).exists():
                raise serializers.ValidationError(
                    f"Username {validated_data["username"]} already exists")
        if "email" in validated_data:
            if User.objects.filter(email=validated_data["email"]).exists():
                raise serializers.ValidationError(
                    f"Email {validated_data["email"]} already exists")
        return validated_data

    def create(self, validated_data: dict[str, Any]) -> Any:
        user = User.objects.create_user(**validated_data)
        author = models.LocalAuthor.objects.create(user=user, **validated_data)
        return author

    def update(self, instance: models.LocalAuthor, validated_data: dict[str, Any]) -> Any:
        user = instance.user
        user.username = validated_data.get("username", user.username)
        user.save()
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image)
        instance.display_name = validated_data.get(
            "display_name", instance.display_name)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.save()


class HostedImageSerializer(serializers.ModelSerializer[models.HostedImage]):
    """
    DRF serializer for HostedImage model.
    """

    class Meta:
        model = models.HostedImage
        fields = ["id", "title", "image", "uploaded_at"]
