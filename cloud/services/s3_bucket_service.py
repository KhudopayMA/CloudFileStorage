import os

import dotenv
import boto3

from cloud.dtos import ResourceMetaDto, DirectoryMetaDto
from cloud.enums import ResourceTypes

dotenv.load_dotenv()


class S3BucketService:

    def __init__(self):
        self.client = self._create_client()

    def _create_client(self):
        client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        )
        return client

    def get_object_meta(self, path: str) -> ResourceMetaDto:
        if path.endswith("/"):
            resource_type = ResourceTypes.DIRECTORY
        else:
            resource_type = ResourceTypes.FILE
        obj = self.client.head_object(
            Bucket="user-files",
            Key=path,
        )
        return ResourceMetaDto(
            path=path[0:path.rfind("/")+1],
            name=path[path.rfind("/")+1:],
            size=obj["ContentLength"],
            type=resource_type
        )

    def get_objects_meta(self, path: str) -> list[ResourceMetaDto | DirectoryMetaDto]:
        response = self.client.list_objects_v2(
            Bucket="user-files",
            Prefix=path,
            Delimiter="/"
        )
        objects = []
        for obj in response.get("Contents"):
            objects.append(
                ResourceMetaDto(
                    path=path,
                    name=obj["Key"],
                    size=obj["Size"],
                    type=ResourceTypes.FILE
                )
            )

        for obj in response.get("CommonPrefixes"):
            objects.append(
                DirectoryMetaDto(
                    path=path,
                    name=obj["Prefix"],
                    type=ResourceTypes.DIRECTORY
                )
            )

        return objects

    def delete_object(self, path: str) -> None:
        self.client.delete_object(Bucket="user-files", Key=path)

    def download_object(self, path: str) -> bytes:
        obj = self.client.get_object(Bucket="user-files", Key=path)
        return obj["Body"].read()

    def upload_object(self, path: str, object_body: bytes, object_content_type: str) -> None:
        self.client.put_object(
            Body=object_body,
            Bucket="user-files",
            Key=path,
            ContentType=object_content_type,
            IfNoneMatch="*"
        )

    def move_object(self, from_path: str, to_path: str) -> None:
        self.client.copy_object(
            Bucket="user-files",
            Key=to_path,
            CopySource={
                "Bucket": "user-files",
                "Key": from_path
            }
        )
        self.delete_object(from_path)


