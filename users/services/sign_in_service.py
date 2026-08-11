from dataclasses import asdict

from django.contrib.auth import authenticate, login
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from users.dtos import UserCredentialsDto


def sign_in_user(user_credentials: UserCredentialsDto, request: Request) -> None:
        user = authenticate(request, **asdict(user_credentials))
        if user is not None:
            login(request, user)
        else:
            raise AuthenticationFailed("Wrong username or password")