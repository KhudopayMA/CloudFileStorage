import logging
from typing import Any

from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed, APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from config.exceptions import ConflictError, NotFound

logger = logging.getLogger(__name__)

def handle_validation_error(exc: APIException, context: dict[str, Any]) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_400_BAD_REQUEST)


def handle_authentication_error(exc: APIException, context: dict[str, Any]) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_401_UNAUTHORIZED)


def handle_conflict_error(exc: APIException, context: dict[str, Any]) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_409_CONFLICT)


def handle_not_found_error(exc: APIException, context: dict[str, Any]) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_404_NOT_FOUND)


exception_mapper = {
    ValidationError: handle_validation_error,
    AuthenticationFailed: handle_authentication_error,
    ConflictError: handle_conflict_error,
    NotFound: handle_not_found_error
}


def custom_exception_handler(exc: APIException, context: dict[str, Any]) -> Response | None:  

    try:
        exc_handler = exception_mapper[type(exc)]
        return exc_handler(exc, context)
    except KeyError:
        response = exception_handler(exc, context)
        logger.error(exc.detail)
        return response
