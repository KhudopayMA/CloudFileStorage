import logging
from dataclasses import asdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.request import Request

from users.dtos.user_credentials_dto import UserCredentialsDto

logger = logging.getLogger(__name__)


def sign_up_user(user_credentials: UserCredentialsDto, request: Request) -> None:
    """
    Service sign-up user
    """
    with transaction.atomic():
        user = User.objects.create_user(**asdict(user_credentials))
        login(request, user)
        logger.info(f"The user {user_credentials.username} has been registered")
