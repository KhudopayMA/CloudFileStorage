from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import exception_handler

from config.exceptions import ConflictError


def handle_validation_error(exc, context) -> Response: # type: ignore[no-untyped-def]
    return Response({'message': exc.detail.values()}, status=status.HTTP_400_BAD_REQUEST)


def handle_authentication_error(exc, context) -> Response: # type: ignore[no-untyped-def]
    return Response({'message': exc.detail}, status=status.HTTP_401_UNAUTHORIZED)


def handle_conflict_error(exc, context) -> Response: # type: ignore[no-untyped-def]
    return Response({'message': exc.detail}, status=status.HTTP_409_CONFLICT)


exception_mapper = {
    ValidationError: handle_validation_error,
    AuthenticationFailed: handle_authentication_error,
    ConflictError: handle_conflict_error
}


def custom_exception_handler(exc, context) -> Response | None: # type: ignore[no-untyped-def]

    try:
        exc_handler = exception_mapper[type(exc)]
        return exc_handler(exc, context)
    except KeyError:
        response = exception_handler(exc, context)
        return response
