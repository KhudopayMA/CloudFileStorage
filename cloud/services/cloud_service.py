import logging

from botocore.exceptions import ClientError

from cloud.services import S3BucketService
from config.exceptions import ConflictError, NotFound

logger = logging.getLogger(__name__)


class CloudService:

    def __init__(self):
        self.s3_service = S3BucketService()

    def create_directory(self, path: str):
        try:
            parent_dir_path = path[0:path.rfind("/")+1]
            self.s3_service.get_object_meta(path=parent_dir_path)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise NotFound("Parent directory not found.") from e
        try:
            self.s3_service.upload_object(
                path=path,
                object_body=b"",
                object_content_type="application/x-director"
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

