import logging
from dataclasses import asdict

from botocore.exceptions import ClientError  #type: ignore[import-untyped]
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.request import Request

from config.exceptions import ConflictError
from storage.services import StorageService
from users.dtos.user_credentials_dto import UserCredentialsDto

logger = logging.getLogger(__name__)


def sign_up_user(user_credentials: UserCredentialsDto, request: Request) -> None:
    """
    Service sign-up user
    """
    with transaction.atomic():
        if User.objects.filter(username=user_credentials.username).exists():
            raise ConflictError("Username already in use.")
        user = User.objects.create_user(**asdict(user_credentials))
        storage_service = StorageService()
        try:
            storage_service.create_directory(path="", user_id=user.id)
            logger.info("Directory user-%-files in s3 was created.", user.id)
        except ClientError as e:
            logger.exception("Error creating directory in s3.")
        login(request, user)
        logger.info("The user %s has been registered", user_credentials.username)
