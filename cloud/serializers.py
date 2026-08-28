from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CreateFolderSerializer(serializers.Serializer[Any]):

    path = serializers.CharField()

    def validate_path(self, path: str) -> str:
        if path is None or not path.endswith("/"):
            raise ValidationError("Path has invalid format")
        return path

