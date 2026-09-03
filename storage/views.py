from dataclasses import asdict

from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from storage.dtos import ResourceMetaDto
from storage.enums import ResourceTypes
from storage.serializers import CreateFolderSerializer
from storage.services import StorageService


class ResourceView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request: Request) -> Response:
        path = request.query_params["path"]
        storage_service = StorageService()
        resource_meta = storage_service.get_resource_meta(path=path, user_id=request.user.id)
        return Response(asdict(resource_meta))

    def post(self, request: Request) -> Response:
        file_obj = request.FILES["object"]
        storage_service = StorageService()
        storage_service.create_file(
            path=request.data["path"],
            user_id=request.user.id,
            file_name=file_obj.name,
            file_body=file_obj.read(),
            file_content_type=file_obj.content_type
        )
        response_body = ResourceMetaDto(
            path=request.data["path"],
            name=file_obj.name,
            size=file_obj.size,
            type=ResourceTypes.FILE
        )
        return Response(asdict(response_body), status=status.HTTP_201_CREATED)

    def delete(self, request: Request) -> Response:
        storage_service = StorageService()
        storage_service.delete_resource(request.query_params["path"], user_id=request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceDownloadView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> FileResponse:
        storage_service = StorageService()
        resource = storage_service.download_resource(request.query_params["path"], user_id=request.user.id)
        return FileResponse(
            resource,
            content_type="application/octet-stream",
            status=status.HTTP_200_OK
        )


class ResourceMoveView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        storage_service = StorageService()
        resource_meta = storage_service.move_resource(
            from_path=request.query_params["from"],
            to_path=request.query_params["to"],
            user_id=request.user.id
        )
        return Response(asdict(resource_meta), status=status.HTTP_200_OK)


class ResourceSearchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        storage_service = StorageService()
        resources_meta = storage_service.search_resources(
            request.query_params["query"], user_id=request.user.id
        )
        response_body = [asdict(resource) for resource in resources_meta]
        return Response(response_body, status=status.HTTP_200_OK)


class DirectoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        storage_service = StorageService()
        path = request.query_params["path"]
        directory_content = storage_service.get_directory_content(path=path, user_id=request.user.id)
        if directory_content is not None:
            response_body = [asdict(obj) for obj in directory_content]
        else: response_body = []
        return Response(response_body, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateFolderSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        path = serializer.validated_data["path"]
        storage_service = StorageService()
        created_dir_meta = storage_service.create_directory(path=path,  user_id=request.user.id)
        return Response(asdict(created_dir_meta), status=status.HTTP_201_CREATED)
