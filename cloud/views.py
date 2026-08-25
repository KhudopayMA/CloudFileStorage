from dataclasses import asdict

from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.serializers import PathSerializer
from cloud.services import S3BucketService


class ResourceView(APIView):

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request: Request) -> Response:
        serializer = PathSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        s3_service = S3BucketService()
        resource_meta = s3_service.get_resource_meta(serializer.validated_data["path"])
        return Response(asdict(resource_meta))

    def post(self, request: Request) -> Response:
        file_obj = request.FILES["file"]
        s3_service = S3BucketService()
        s3_service.upload_resource(
            path=request.query_params["path"],
            file_body=file_obj.read(),
            file_content_type=file_obj.content_type
        )
        return Response(status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        s3_service = S3BucketService()
        s3_service.delete_resource(request.query_params["path"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceDownloadView(APIView):

    permission_classes = [AllowAny]

    def get(self, request: Request) -> FileResponse:
        s3_service = S3BucketService()
        resource = s3_service.download_resource(request.query_params["path"])
        return FileResponse(resource, content_type="application/octet-stream", status=status.HTTP_200_OK)


class ResourceMoveView(APIView):

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        s3_service = S3BucketService()
        s3_service.move_resource(from_path=request.query_params["from"], to_path=request.query_params["to"])
        return Response(status=status.HTTP_200_OK)
