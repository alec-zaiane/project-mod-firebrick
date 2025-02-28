from typing import Optional

from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request


from socialnetwork.utils.user_control_decorator import user_controller, user_control
from socialnetwork import serializers

# This file is for only API views, standardized to our API spec
# see https://uofa-cmput404.github.io/general/project.html#api-endpoints
