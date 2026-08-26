import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms.models import model_to_dict

from cloud.dtos import ResourceMetaDto
from cloud.services import S3BucketService
from cloud.models import Folder, File
from config.exceptions import ConflictError

logger = logging.getLogger(__name__)


class CloudService:

    def __init__(self, s3_service: S3BucketService):
        self.s3_service = s3_service

    # def get_resource_meta(self, path: str):
    #     self.s3_service.get_resource_meta(path)

    def upload_resource(self, path: str, file_body: bytes, file_content_type: str) -> ResourceMetaDto:
        parent_folder_path = path[0:path.rfind("/")]
        file_name = path[path.rfind("/") + 1:]
        with transaction.atomic():
            if self._is_folder_exists(parent_folder_path):
                parent_folder = Folder.objects.get(full_name=path[0:path.rfind("/")+1])
            else:
                folders = parent_folder_path.split("/")
                parent_folder = None
                for folder in folders:
                    folder = Folder.objects.get_or_create(
                        name=folder,
                        folder=parent_folder
                    )
                    parent_folder = folder

            file = File.objects.create(
                name=file_name,
                folder=parent_folder.id,
                path=parent_folder_path,
                size=len(file_body),
            )
            try:
                file.validate_unique()
                file.save()
            except ValidationError as e:
                raise ConflictError(
                    f"File with name {file_name} already exists on the path {parent_folder_path}"
                ) from e
            self.s3_service.upload_object(path=path, file_body=file_body, file_content_type=file_content_type)
            return ResourceMetaDto(
                path=path[0:path.rfind("/") + 1],
                name=path[path.rfind("/") + 1:],
                size=len(file_body),
                type="FILE"
            )

    def _is_folder_exists(self, path: str) -> bool:
        # TODO think about folder logic
        folders = path.split("/")
        parent_folder = None
        for folder in folders:
            folder = Folder.objects.get_or_create(
                name=folder,
                folder=parent_folder
            )
            parent_folder = folder
        return parent_folder
        # return Folder.objects.exists(full_name=path[0:path.rfind("/")+1])
