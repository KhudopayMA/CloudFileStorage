import os

import dotenv
import boto3

from cloud.dtos import ResourceMetaDto

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

    def get_resource_meta(self, path: str) -> ResourceMetaDto:
        if path.endswith("/"):
            objects = self.client.list_objects_v2(
                Bucket="user-files",
                Prefix=path
            )
            for obj in objects["Contents"]:
                print(obj)

        obj = self.client.head_object(Bucket="user-files", Key=path)
        return ResourceMetaDto(
            path=path[0:path.rfind("/")+1],
            name=path[path.rfind("/")+1:],
            size=obj["ContentLength"],
            type="FILE"
        )

    def delete_resource(self, path: str) -> None:
        self.client.delete_object(Bucket="user-files", Key=path)

    def download_resource(self, path: str) -> bytes:
        obj = self.client.get_object(Bucket="user-files", Key=path)
        return obj["Body"].read()

    def upload_resource(self, path: str, file_body: bytes, file_content_type: str):
        self.client.put_object(
            Body=file_body,
            Bucket="user-files",
            Key=path,
            ContentType=file_content_type
        )

    def move_resource(self, from_path: str, to_path: str) -> None:
        self.client.copy_object(
            Bucket="user-files",
            Key=to_path,
            CopySource={
                "Bucket": "user-files",
                "Key": from_path
            }
        )
        self.delete_resource(from_path)


