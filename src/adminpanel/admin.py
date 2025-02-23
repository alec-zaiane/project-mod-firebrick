from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.AuthorJoinRequest)
admin.site.register(models.HostedImage)