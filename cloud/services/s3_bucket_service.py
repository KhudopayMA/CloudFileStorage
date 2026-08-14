import os

import dotenv
import boto3

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

    def get_resource_meta(self, path: str):
        attributes = ['ETag', 'Checksum', 'ObjectParts', 'StorageClass', 'ObjectSize']
        # object_attributes = self.client.get_object_attributes(
        #     Bucket="user-files",
        #     Key=path,
        #     ObjectAttributes=attributes
        # )
        # return object_attributes
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket="user-files"):
            for obj in page.get('Contents', ):
                print(obj['Key'])

    # def create_file(self, file, path):
    #     self.client.upload_file(f, "user-files", "test.txt")
    #
    # def delete_file(self):
    #     pass
    #
    # def rename_file(self):
    #     pass
    #
    # def rename_folder(self):
    #     pass
    #
    # def get_structure(self):
    #     response = self.client.list_objects_v2(Bucket='user-files', Prefix='user-1-files')
    #     for obj in response["Contents"]:
    #         print(obj["Key"])

# s3 = S3BucketService()
# s3.get_structure()
# s3.create_file()
