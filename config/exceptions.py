from rest_framework import status
from rest_framework.exceptions import APIException


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict"
    default_code = "conflict"


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found"
    default_code = "not_found"
