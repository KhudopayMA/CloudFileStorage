import io
from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from storage.enums import ResourceTypes


@pytest.mark.django_db
class TestResourceView(TestCase):
    client = APIClient()

    def setUp(self) -> None:
        data = {"username": "user1", "password": "testpassword12345"}
        self.client.post("/api/auth/sign-up", data=data, extra={"format": "json"})
        self.user = User.objects.get(username=data["username"])
        self.client.force_authenticate(user=self.user)

    def test_create_file(self) -> None:
        file = SimpleUploadedFile(
            name="test.txt",
            content=b"Test file"
        )
        post_response = self.client.post(
            "/api/resource",
            data={
                "object": file,
                "path": ""
            },
            extra={"format": "json"}
        )
        assert post_response.status_code == 201
        assert post_response.data["path"] == ""
        assert post_response.data["name"] == file.name
        assert post_response.data["size"] == file.size
        assert post_response.data["type"] == ResourceTypes.FILE

        get_response = self.client.get(
            "/api/resource",
            query_params={
                "path": f"{file.name}"
            },
            extra={"format": "json"}
        )

        assert get_response.status_code == 200
        assert get_response.data["path"] == ""
        assert get_response.data["name"] == file.name
        assert get_response.data["size"] == file.size
        assert get_response.data["type"] == ResourceTypes.FILE

    def test_delete_file(self) -> None:
        file = SimpleUploadedFile(
            name="test.txt",
            content=b"Test file"
        )
        post_response = self.client.post(
            "/api/resource",
            data={
                "object": file,
                "path": ""
            },
            extra={"format": "json"}
        )
        assert post_response.status_code == 201
        assert post_response.data["path"] == ""
        assert post_response.data["name"] == file.name
        assert post_response.data["size"] == file.size
        assert post_response.data["type"] == ResourceTypes.FILE

        delete_response = self.client.delete(
            "/api/resource",
            query_params={
                "path": f"{file.name}"
            },
            extra={"format": "json"}
        )

        assert delete_response.status_code == 204

        get_response = self.client.get(
            "/api/resource",
            query_params={
                "path": f"{file.name}"
            },
            extra={"format": "json"}
        )

        assert get_response.status_code == 404
        assert get_response.data["message"] == "Resource not found."
