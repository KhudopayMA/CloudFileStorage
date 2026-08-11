from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response

from config.exceptions import ConflictError

def handle_validation_error(exc, context) -> Response:
    return Response({'message': exc.detail.values()}, status=status.HTTP_400_BAD_REQUEST)

def handle_authentication_error(exc, context) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_401_UNAUTHORIZED)

def handle_conflict_error(exc, context) -> Response:
    return Response({'message': exc.detail}, status=status.HTTP_409_CONFLICT)

exception_mapper = {
    ValidationError: handle_validation_error,
    AuthenticationFailed: handle_authentication_error,
    ConflictError: handle_conflict_error
}

def custom_exception_handler(exc, context):

    try:
        exc_handler = exception_mapper[type(exc)]
        return exc_handler(exc, context)
    except KeyError:
        #TODO add logs here and for every handler
        return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)