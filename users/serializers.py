from typing import Any

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers

from config.exceptions import ConflictError

english_letter_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9]+$",
    message="Only English letters and numbers are allowed.",
)


class SignUpSerializer(serializers.Serializer[Any]):
    username = serializers.CharField(
        required=True,
        max_length=20,
        min_length=5,
        validators=[
            english_letter_validator,
        ],
        error_messages={
            "min_length": "Username must be at least 5 characters.",
            "max_length": "Username must be at most 100 characters.",
        },
    )
    password = serializers.CharField(required=True, max_length=20, min_length=5)

    def validate_username(self, username: str) -> str:
        if User.objects.filter(username=username).exists():
            raise ConflictError("Username already in use.")
        return username


class SignInSerializer(serializers.Serializer[Any]):
    username = serializers.CharField(
        required=True,
        max_length=20,
        min_length=5,
        validators=[english_letter_validator],
        error_messages={
            "min_length": "Username must be at least 5 characters.",
            "max_length": "Username must be at most 100 characters.",
        },
    )
    password = serializers.CharField(required=True, max_length=20)
