import logging
from dataclasses import asdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.request import Request
from botocore.exceptions import ClientError

from config.exceptions import ConflictError
from users.dtos.user_credentials_dto import UserCredentialsDto
from storage.services import StorageService

logger = logging.getLogger(__name__)


def sign_up_user(user_credentials: UserCredentialsDto, request: Request) -> None:
    """
    Service sign-up user
    """
    with transaction.atomic():
        if User.objects.filter(username=user_credentials.username).exists():
            raise ConflictError(f"Username already in use.")
        user = User.objects.create_user(**asdict(user_credentials))
        try:
            storage_service = StorageService()
            storage_service.create_directory(path="", user_id=user.id)
            logger.info(f"Directory user-{user.id}-files in s3 was created.")
        except ClientError as e:
            logger.error("Error creating directory in s3.", exc_info=e)
        login(request, user)
        logger.info("The user %s has been registered", user_credentials.username)
