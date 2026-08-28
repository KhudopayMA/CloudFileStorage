import logging
import zipfile
import threading

from botocore.exceptions import ClientError

from cloud.dtos import ResourceMetaDto
from cloud.services import S3BucketService
from config.exceptions import ConflictError, NotFound

logger = logging.getLogger(__name__)


class CloudService:

    def __init__(self):
        self.s3_service = S3BucketService()

    def create_directory(self, path: str):
        try:
            if len(path.strip("/").split("/")) > 1:
                parent_dir_path = path[0:path.find("/")+1]
                self.s3_service.get_object_meta(path=parent_dir_path)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise NotFound("Parent directory not found.") from e
        try:
            self.s3_service.upload_object(
                path=path,
                object_body=b"",
                object_content_type="application/x-directory"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":
                raise ConflictError("Directory already exists.") from e

    def get_directory_content(self, path: str):
        try:
            self.s3_service.get_object_meta(path=path)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise NotFound("Directory not found.") from e
        return self.s3_service.get_objects_meta(path=path)

    def create_file(
        self,
        path: str,
        file_name: str,
        file_content_type: str,
        file_body: bytes
    ):
        directories = path.strip("/").split("/")
        current_directory = ""
        for directory in directories:
            current_directory += directory + "/"
            try:
                self.s3_service.get_object_meta(path=current_directory)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    self.create_directory(current_directory)
        try:
            self.s3_service.upload_object(
                path=path + file_name,
                object_body=file_body,
                object_content_type=file_content_type
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":
                raise ConflictError("File already exists.") from e

    def get_resource(self, path: str) -> ResourceMetaDto:
        # TODO обавить получение файлов из директории и формирование zip
        # if path.endswith("/"):
        #

        file = self.s3_service.download_object(path)
        return file

    def move_resource(self, from_path: str, to_path: str):
        threading.Thread