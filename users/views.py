from django.contrib.auth import logout
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .dtos import UserCredentialsDto
from .serializers import SignUpSerializer, SignInSerializer
from .services import sign_up_user, sign_in_user


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_credentials = UserCredentialsDto(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        sign_up_user(user_credentials, request)
        response = Response(serializer.data["username"], status=status.HTTP_201_CREATED)
        return response

class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_credentials = UserCredentialsDto(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        sign_in_user(user_credentials, request)
        response = Response(
            {
                "username": user_credentials.username
            },
            status=status.HTTP_200_OK
        )
        return response

class SignOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request) -> Response:
        return Response({"username": request.user.username})
