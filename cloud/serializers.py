from django.core.validators import RegexValidator
from rest_framework import serializers

# path_validator = RegexValidator(
#         regex=r'/$',
#         message='Path must end with /',
#     )


class PathSerializer(serializers.Serializer):
    path = serializers.CharField(
        # validators=[path_validator]
    )

# class ResourceSerializer(serializers.Serializer):
