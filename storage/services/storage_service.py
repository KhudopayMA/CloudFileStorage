import logging
import zipfile
from io import BytesIO

from rest_framework.exceptions import APIException

from config.exceptions import ConflictError, NotFound
from storage.dtos import DirectoryMetaDto, ResourceMetaDto
from storage.enums import ResourceTypes
from storage.services import S3Service

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.s3_service = S3Service()

    def get_resource_meta(
        self, path: str, user_id: int
    ) -> ResourceMetaDto | DirectoryMetaDto:
        user_path = f"user-{user_id}-files/" + path
        return self.s3_service.get_object_meta(path=user_path)

    def create_directory(self, path: str, user_id: int) -> DirectoryMetaDto:
        user_path = f"user-{user_id}-files/" + path
        if path:
            parent_dir_path = user_path[
                0 : user_path.rfind("/", 0, len(user_path) - 1) + 1
            ]
            try:
                self.s3_service.get_object_meta(path=parent_dir_path)
            except NotFound as e:
                raise NotFound("Parent directory not found.") from e
        try:
            self.s3_service.upload_object(
                path=user_path,
                object_body=b"",
                object_content_type="application/x-directory",
            )
            return DirectoryMetaDto(
                path=path[path.find("/") : path.rfind("/", 0, len(path) - 1) + 1],
                name=path[path.rfind("/", 0, len(path) - 1) + 1 : len(path) - 1],
                type=ResourceTypes.DIRECTORY,
            )
        except ConflictError as e:
            logger.info("Directory %s already exist", user_path)
            raise ConflictError("Directory already exists.") from e
        except APIException as e:
            logger.exception("Failed to create directory %s in s3", user_path)
            raise APIException() from e

    def get_directory_content(
        self, path: str, user_id: int
    ) -> list[ResourceMetaDto | DirectoryMetaDto]:
        user_path = f"user-{user_id}-files/" + path
        try:
            return self.s3_service.get_directory_objects(path=user_path)
        except NotFound as e:
            logger.info("Directory %s is empty", user_path)
            raise NotFound("Directory not found.") from e
        except APIException as e:
            raise e

    def create_file(
        self,
        path: str,
        user_id: int,
        file_name: str,
        file_content_type: str,
        file_body: bytes,
    ) -> None:
        user_path = f"user-{user_id}-files/" + path
        directories = path.strip("/").split("/")
        current_directory = ""
        for directory in directories:
            current_directory += directory + "/"
            try:
                self.s3_service.get_object_meta(path=current_directory)
            except NotFound:
                self.create_directory(current_directory, user_id)
        try:
            self.s3_service.upload_object(
                path=user_path + file_name,
                object_body=file_body,
                object_content_type=file_content_type,
            )
        except ConflictError as e:
            raise ConflictError("File already exists.") from e

    def download_resource(self, path: str, user_id: int) -> bytes | BytesIO:
        user_path = f"user-{user_id}-files/" + path
        if user_path.endswith("/"):
            files = self.s3_service.download_objects(user_path)
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in files:
                    zf.writestr(file.name, file.content)
            buffer.seek(0)
            return buffer
        file_body = self.s3_service.download_object(path=user_path)
        return file_body

    def delete_resource(self, path: str, user_id: int) -> None:
        user_path = f"user-{user_id}-files/" + path
        self.s3_service.delete_object(path=user_path)

    def move_resource(
        self, from_path: str, to_path: str, user_id: int
    ) -> ResourceMetaDto | DirectoryMetaDto:
        user_from_path = f"user-{user_id}-files/" + from_path
        user_to_path = f"user-{user_id}-files/" + to_path
        self.s3_service.move_object(from_path=user_from_path, to_path=user_to_path)
        return self.s3_service.get_object_meta(path=user_to_path)

    def search_resources(
        self, substring: str, user_id: int
    ) -> list[ResourceMetaDto | DirectoryMetaDto]:
        user_dir_path = f"user-{user_id}-files/"
        user_resources = self.s3_service.search_objects(user_dir_path)
        suitable_resources = []
        for resource in user_resources:
            if substring in resource.path + resource.name:
                suitable_resources.append(resource)
        return suitable_resources
