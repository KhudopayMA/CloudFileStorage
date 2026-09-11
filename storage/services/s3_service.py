import logging
from typing import cast

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from rest_framework.exceptions import APIException

from config.exceptions import ConflictError, NotFound
from config.settings import AWS_ACCESS_KEY_ID, AWS_ENDPOINT_URL, AWS_SECRET_ACCESS_KEY
from storage.dtos import DirectoryMetaDto, FileDto, ResourceMetaDto
from storage.enums import ResourceTypes

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self) -> None:
        self.client = self._create_client()  # type: ignore[no-untyped-call]

    def _create_client(self):  # type: ignore[no-untyped-def]
        client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=AWS_ENDPOINT_URL,
        )
        return client

    def get_object_meta(self, path: str) -> ResourceMetaDto | DirectoryMetaDto:
        try:
            obj = self.client.head_object(
                Bucket="user-files",
                Key=path,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.warning("Resource %s does not exist", path)
                raise NotFound("Resource not found.") from e
            raise e
        if path.endswith("/"):
            return DirectoryMetaDto(
                path=path[path.find("/") : path.rfind("/", 0, len(path) - 1) + 1],
                name=path[path.rfind("/", 0, len(path) - 1) + 1 : len(path) - 1],
                type=ResourceTypes.DIRECTORY,
            )
        else:
            return ResourceMetaDto(
                path=path[path.find("/") + 1 : path.rfind("/") + 1],
                name=path[path.rfind("/") + 1 :],
                size=obj["ContentLength"],
                type=ResourceTypes.FILE,
            )

    def get_directory_objects(
        self, path: str
    ) -> list[ResourceMetaDto | DirectoryMetaDto]:
        try:
            response = self.client.list_objects_v2(
                Bucket="user-files", Prefix=path, Delimiter="/"
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise NotFound() from e
            else:
                raise APIException() from e
        objects: list[ResourceMetaDto | DirectoryMetaDto] = []
        response.get("Contents")
        for obj in response.get("Contents"):
            if obj["Key"] != path:
                objects.append(
                    ResourceMetaDto(
                        path=path[path.find("/") + 1 : path.rfind("/") + 1],
                        name=obj["Key"][obj["Key"].rfind("/") + 1 :],
                        size=obj["Size"],
                        type=ResourceTypes.FILE,
                    )
                )
        if "CommonPrefixes" in response:
            for obj in response.get("CommonPrefixes"):
                objects.append(
                    DirectoryMetaDto(
                        path=path[path.find("/") + 1 : path.rfind("/") + 1],
                        name=obj["Prefix"][
                            obj["Prefix"].rfind("/", 0, len(obj["Prefix"]) - 1) + 1 :
                        ],
                        type=ResourceTypes.DIRECTORY,
                    )
                )
        return objects

    def search_objects(self, path: str) -> list[ResourceMetaDto | DirectoryMetaDto]:
        response = self.client.list_objects_v2(Bucket="user-files", Prefix=path)
        objects: list[ResourceMetaDto | DirectoryMetaDto] = []
        for obj in response.get("Contents"):
            if obj["Key"] != path:
                if obj["Key"].endswith("/"):
                    objects.append(
                        DirectoryMetaDto(
                            path=path[path.find("/") + 1 : path.rfind("/") + 1],
                            name=obj["Key"][
                                obj["Key"].rfind("/", 0, len(obj["Key"]) - 1) + 1 :
                            ],
                            type=ResourceTypes.DIRECTORY,
                        )
                    )
                else:
                    objects.append(
                        ResourceMetaDto(
                            path=path[path.find("/") + 1 : path.rfind("/") + 1],
                            name=obj["Key"][obj["Key"].rfind("/") + 1 :],
                            size=obj["Size"],
                            type=ResourceTypes.FILE,
                        )
                    )
        return objects

    def delete_object(self, path: str) -> None:
        self.client.delete_object(Bucket="user-files", Key=path)

    def download_object(self, path: str) -> bytes:
        obj = self.client.get_object(Bucket="user-files", Key=path)
        return cast(bytes, obj["Body"].read())

    def download_objects(self, prefix: str) -> list[FileDto]:
        objects = self.client.list_objects_v2(
            Bucket="user-files", Prefix=prefix, Delimiter="/"
        )
        objects_content = []
        for obj in objects["Contents"]:
            if not obj["Key"].endswith("/"):
                obj_content = self.download_object(obj["Key"])
                objects_content.append(
                    FileDto(
                        name=obj["Key"][obj["Key"].rfind("/") + 1 :],
                        content=obj_content,
                    )
                )
        return objects_content

    def upload_object(
        self, path: str, object_body: bytes, object_content_type: str
    ) -> None:
        try:
            self.client.put_object(
                Body=object_body,
                Bucket="user-files",
                Key=path,
                ContentType=object_content_type,
                IfNoneMatch="*",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "PreconditionFailed":
                raise ConflictError() from e
            else:
                raise APIException() from e

    def move_object(self, from_path: str, to_path: str) -> None:
        if from_path.endswith("/"):
            objects = self.client.list_objects_v2(
                Bucket="user-files",
                Prefix=from_path,
            )
            for obj in objects["Contents"]:
                if obj["Key"] != from_path:
                    new_path = (
                        to_path
                        + obj["Key"][
                            obj["Key"].rfind("/", 0, len(obj["Key"]) - 1) + 1:
                        ]
                    )
                else:
                    new_path = to_path
                self.client.copy_object(
                    Bucket="user-files",
                    Key=new_path,
                    CopySource={"Bucket": "user-files", "Key": obj["Key"]},
                )
                self.delete_object(obj["Key"])
        else:
            self.client.copy_object(
                Bucket="user-files",
                Key=to_path,
                CopySource={"Bucket": "user-files", "Key": from_path},
            )
            self.delete_object(from_path)
