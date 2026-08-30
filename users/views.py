from django.contrib.auth import logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dtos import UserCredentialsDto
from .serializers import SignInSerializer, SignUpSerializer
from .services import sign_in_user, sign_up_user


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_credentials = UserCredentialsDto(
            username=request.data["username"],
            password=request.data["password"],
        )
        sign_up_user(user_credentials, request)
        response = Response(
            {"username": request.data["username"]}, status=status.HTTP_201_CREATED
        )
        return response


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_credentials = UserCredentialsDto(
            username=request.data["username"],
            password=request.data["password"],
        )
        sign_in_user(user_credentials, request)
        response = Response({"username": request.data["username"]}, status=status.HTTP_200_OK)
        return response


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response({"username": request.user.username})
