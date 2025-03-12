"""Custom validators for rest_framework serializers :)"""

from typing import Any


from rest_framework.serializers import ValidationError

# https://www.django-rest-framework.org/api-guide/validators/#writing-custom-validators


class ExactlyEqualTo:
    def __init__(self, base: Any):
        self.base = base

    def __call__(self, value: Any) -> None:
        if value != self.base:
            raise ValidationError(
                f"Value must be exactly equal to {self.base}")


class IsInSet:
    def __init__(self, base: set[Any] | list[Any]):
        self.base = base

    def __call__(self, value: Any) -> None:
        if value not in self.base:
            raise ValidationError(
                f"Value must be in set {self.base}, got {value}"
            )


class ContainsValidator:
    def __init__(self, base: Any):
        self.base = base

    def __call__(self, value: Any) -> None:
        if self.base not in value:
            raise ValidationError(
                f"Value must contain {self.base}, got {value}"
            )
