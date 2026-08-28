from dataclasses import asdict

from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.dtos import ResourceMetaDto, DirectoryMetaDto
from cloud.enums import ResourceTypes
from cloud.serializers import CreateFolderSerializer
from cloud.services import S3BucketService
from cloud.services.cloud_service import CloudService


class ResourceView(APIView):

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request: Request) -> Response:
        path = request.data["path"]
        s3_service = S3BucketService()
        resource_meta = s3_service.get_object_meta(path)
        return Response(asdict(resource_meta))

    def post(self, request: Request) -> Response:
        file_obj = request.FILES["file"]
        cloud_service = CloudService()
        cloud_service.create_file(
            path=request.query_params["path"],
            file_name=file_obj.name,
            file_body=file_obj.read(),
            file_content_type=file_obj.content_type
        )
        response_body = ResourceMetaDto(
            path=request.query_params["path"],
            name=file_obj.name,
            size=file_obj.size,
            type=ResourceTypes.FILE
        )
        return Response(asdict(response_body), status=status.HTTP_200_OK)

    # def delete(self, request: Request) -> Response:
    #     s3_service = S3BucketService()
    #     s3_service.delete_resource(request.query_params["path"])
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceDownloadView(APIView):

    permission_classes = [AllowAny]

    def get(self, request: Request) -> FileResponse:
        cloud_service = CloudService()
        resource = cloud_service.get_resource(request.query_params["path"])
        return FileResponse(
            resource,
            content_type="application/octet-stream",
            status=status.HTTP_200_OK
        )


class ResourceMoveView(APIView):

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        s3_service = S3BucketService()
        s3_service.move_resource(from_path=request.query_params["from"], to_path=request.query_params["to"])
        return Response(status=status.HTTP_200_OK)


class DirectoryView(APIView):

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        cloud_service = CloudService()
        path = request.query_params["path"]
        directory_content = cloud_service.get_directory_content(path=path)
        response_body = [asdict(obj) for obj in directory_content]
        return Response(response_body, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateFolderSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        path = serializer.validated_data["path"]
        cloud_service = CloudService()
        cloud_service.create_directory(path)
        response_body = DirectoryMetaDto(
            path=path[0:path.rfind("/")+1],
            name=path[path.rfind("/")+1:],
            type=ResourceTypes.FILE
        )
        return Response(asdict(response_body), status=status.HTTP_201_CREATED)
