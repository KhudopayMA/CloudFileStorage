import logging
import zipfile
from io import BytesIO

from botocore.exceptions import ClientError
from rest_framework.exceptions import APIException

from storage.dtos import DirectoryMetaDto
from storage.enums import ResourceTypes
from storage.services import S3Service
from config.exceptions import ConflictError, NotFound

logger = logging.getLogger(__name__)


class StorageService:

    def __init__(self):
        self.s3_service = S3Service()

    def create_directory(self, path: str, user_id: int) -> DirectoryMetaDto:
        user_path = f"user-{user_id}-files/" + path
        if path:
            parent_dir_path = user_path[0:user_path.find("/") + 1]
            try:
                self.s3_service.get_object_meta(path=parent_dir_path)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    logger.warning(f"Directory {parent_dir_path} does not exist")
                    raise NotFound("Parent directory not found.") from e
                else:
                    logger.error(f"Failed to found directory {parent_dir_path} in s3", exc_info=e)
                    raise APIException() from e
                # TODO рейзить ошибку для 500 кода
        try:
            self.s3_service.upload_object(
                path=user_path,
                object_body=b"",
                object_content_type="application/x-directory"
            )
            return DirectoryMetaDto(
                path=user_path,
                name=path[path.rfind("/")+1:],
                type=ResourceTypes.FILE
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":
                logger.info(f"Directory {user_path} already exist")
                raise ConflictError("Directory already exists.") from e
            else:
                logger.error(f"Failed to create directory {user_path} in s3", exc_info=e)
                raise APIException() from e
            # TODO рейзить ошибку для 500 кода

    def get_directory_content(self, path: str, user_id: int):
        user_path = f"user-{user_id}-files/" + path
        try:
            return self.s3_service.get_objects_meta(path=user_path)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise NotFound("Directory not found.") from e

    def create_file(
        self,
        path: str,
        user_id: int,
        file_name: str,
        file_content_type: str,
        file_body: bytes
    ):
        user_path = f"user-{user_id}-files/" + path
        directories = user_path.strip("/").split("/")
        current_directory = ""
        for directory in directories:
            current_directory += directory + "/"
            try:
                self.s3_service.get_object_meta(path=current_directory)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    self.create_directory(current_directory, user_id)
        try:
            self.s3_service.upload_object(
                path=user_path + file_name,
                object_body=file_body,
                object_content_type=file_content_type
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":
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

    def delete_resource(self, path: str, user_id: int):
        user_path = f"user-{user_id}-files/" + path
        self.s3_service.delete_object(path=user_path)

    # def get_resource(self, path: str) -> ResourceMetaDto:
    #     # TODO обавить получение файлов из директории и формирование zip
    #     # if path.endswith("/"):
    #     #
    #
    #     file = self.s3_service.download_object(path)
    #     return file

    # def move_resource(self, from_path: str, to_path: str):
    #     pass