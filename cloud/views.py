from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.serializers import PathSerializer
from cloud.services import S3BucketService


class ResourceView(APIView):

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        serializer = PathSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        s3_service = S3BucketService()
        resource_meta = s3_service.get_resource_meta(serializer.validated_data["path"])
        return Response(asdict(resource_meta))

    def delete(self, request: Request) -> Response:
        s3_service = S3BucketService()
        s3_service.delete_resource(request.query_params["path"])
        return Response(status=status.HTTP_204_NO_CONTENT)
