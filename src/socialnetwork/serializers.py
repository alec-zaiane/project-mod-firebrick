from rest_framework import serializers
from . import models

# https://stackoverflow.com/questions/53687071/django-rest-framework-not-null-constraint-failed
class PostSerializer(serializers.ModelSerializer[models.Post]):
    author = serializers.PrimaryKeyRelatedField(many=False, queryset=models.LocalAuthor.objects.all())


class PostTextBasedSerializer(PostSerializer):
    class Meta:
        model = models.PostTextBased
        fields = ["content", "author", "visibility_type", "post_type"]