import logging
from dataclasses import asdict

from django.contrib.auth import authenticate, login
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from users.dtos import UserCredentialsDto

logger = logging.getLogger(__name__)


def sign_in_user(user_credentials: UserCredentialsDto, request: Request) -> None:
    """
    Service sign-in user
    """
    user = authenticate(request, **asdict(user_credentials))
    if user is not None:
        login(request, user)
        logger.info(f"The user {user_credentials.username} is logged in")
    else:
        logger.info(f"The user {user_credentials.username} failed to log in")
        raise AuthenticationFailed("Wrong username or password")
