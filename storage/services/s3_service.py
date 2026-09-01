import os

import dotenv
import boto3

from storage.dtos import ResourceMetaDto, DirectoryMetaDto, FileDto
from storage.enums import ResourceTypes

dotenv.load_dotenv()


class S3Service:

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

    def get_object_meta(self, path: str) -> ResourceMetaDto | DirectoryMetaDto:
        obj = self.client.head_object(
            Bucket="user-files",
            Key=path,
        )
        if path.endswith("/"):
            return DirectoryMetaDto(
                path=path[path.find("/"):path.rfind("/", 0, len(path) - 1)+1],
                name=path[path.rfind("/", 0, len(path) - 1) + 1:len(path)-1],
                type=ResourceTypes.DIRECTORY
            )
        else:
            return ResourceMetaDto(
                path=path[path.find("/") + 1:path.rfind("/") + 1],
                name=path[path.rfind("/") + 1:],
                size=obj["ContentLength"],
                type=ResourceTypes.FILE
            )

    def get_objects_meta(self, path: str, delimiter: str = "") -> list[ResourceMetaDto | DirectoryMetaDto]:
        response = self.client.list_objects_v2(
            Bucket="user-files",
            Prefix=path,
            Delimiter=delimiter
        )
        objects = []
        for obj in response.get("Contents"):
            if obj["Key"] != path:
                if obj["Key"].endswith("/"):
                    objects.append(DirectoryMetaDto(
                            path=path[path.find("/")+1:path.rfind("/")+1],
                            name=obj["Key"][obj["Key"].rfind("/", 0, len(obj["Key"])-1)+1:],
                            type=ResourceTypes.DIRECTORY
                        )
                    )
                else:
                    objects.append(
                        ResourceMetaDto(
                            path=path[path.find("/")+1:path.rfind("/")+1],
                            name=obj["Key"][obj["Key"].rfind("/")+1:],
                            size=obj["Size"],
                            type=ResourceTypes.FILE
                        )
                    )
        if "CommonPrefixes" in response:
            for obj in response.get("CommonPrefixes"):
                objects.append(
                    DirectoryMetaDto(
                        path=path[path.find("/")+1:path.rfind("/")+1],
                        name=obj["Prefix"][obj["Prefix"].rfind("/", 0, len(obj["Prefix"])-1)+1:],
                        type=ResourceTypes.DIRECTORY
                    )
                )

        return objects

    def delete_object(self, path: str) -> None:
        self.client.delete_object(Bucket="user-files", Key=path)

    def download_object(self, path: str) -> bytes:
        obj = self.client.get_object(Bucket="user-files", Key=path)
        return obj["Body"].read()

    def download_objects(self, prefix: str) -> list[FileDto]:
        objects = self.client.list_objects_v2(
            Bucket="user-files",
            Prefix=prefix,
            Delimiter="/"
        )
        objects_content = []
        for obj in objects["Contents"]:
            if not obj["Key"].endswith("/"):
                obj_content = self.download_object(obj["Key"])
                objects_content.append(
                    FileDto(
                        name=obj["Key"][obj["Key"].rfind("/")+1:],
                        content=obj_content,
                    )
                )
        return objects_content

    def upload_object(self, path: str, object_body: bytes, object_content_type: str) -> None:
        self.client.put_object(
            Body=object_body,
            Bucket="user-files",
            Key=path,
            ContentType=object_content_type,
            IfNoneMatch="*"
        )

    def move_object(self, from_path: str, to_path: str) -> None:
        if from_path.endswith("/"):
            objects = self.client.list_objects_v2(
                Bucket="user-files",
                Prefix=from_path,
            )
            for obj in objects["Contents"]:
                if obj["Key"] != from_path:
                    new_path = to_path + obj["Key"][obj["Key"].rfind("/", 0, len(obj["Key"])-1)+1:]
                else:
                    new_path = to_path
                self.client.copy_object(
                    Bucket="user-files",
                    Key=new_path,
                    CopySource={
                        "Bucket": "user-files",
                        "Key": obj["Key"]
                    }
                )
                self.delete_object(obj["Key"])
        else:
            self.client.copy_object(
                Bucket="user-files",
                Key=to_path,
                CopySource={
                    "Bucket": "user-files",
                    "Key": from_path
                }
            )
            self.delete_object(from_path)


