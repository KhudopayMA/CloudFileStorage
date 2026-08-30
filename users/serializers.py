from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

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
    password = serializers.CharField(
        max_length=20, min_length=5, write_only=True, required=True
    )

    def validate_password(self, password: str) -> str :
        try:
            validate_password(password)
            return password
        except ValidationError as e:
            raise serializers.ValidationError(e.messages) from e


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
    password = serializers.CharField(
        max_length=20, min_length=5, write_only=True, required=True
    )

    def validate_password(self, password: str) -> str:
        try:
            validate_password(password)
            return password
        except ValidationError as e:
            raise serializers.ValidationError(e.messages) from e
