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
        logger.info("The user %s is logged in", user_credentials.username)
    else:
        logger.info("The user %s failed to log in", user_credentials.username)
        raise AuthenticationFailed("Wrong username or password")
