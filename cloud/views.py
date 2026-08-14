from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.serializers import PathSerializer
from cloud.services import S3BucketService


class ResourceView(APIView):

    def get(self, request: Request) -> Response:
        serializer = PathSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        s3_service = S3BucketService()
        s3_service.get_resource_meta(serializer.validated_data["path"])