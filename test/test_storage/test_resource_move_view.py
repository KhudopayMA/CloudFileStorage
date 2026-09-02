from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import force_authenticate, APIClient

from storage.enums import ResourceTypes


@pytest.mark.django_db
class TestResourceView(TestCase):
    client = APIClient()

    def setUp(self) -> None:
        data = {"username": "user1", "password": "testpassword12345"}
        self.client.post("/api/auth/sign-up", data=data, extra={"format": "json"})
        self.user = User.objects.get(username=data["username"])
        self.client.force_authenticate(user=self.user)

    def test_rename_file(self):
        file = SimpleUploadedFile(
            name="test.txt",
            content=b"Test file"
        )
        create_file_response = self.client.post(
            "/api/resource",
            data={
                "object": file,
                "path": ""
            },
            extra={"format": "json"}
        )
        assert create_file_response.status_code == 201
        assert create_file_response.data["path"] == ""
        assert create_file_response.data["name"] == file.name
        assert create_file_response.data["size"] == file.size
        assert create_file_response.data["type"] == ResourceTypes.FILE

        move_file_response = self.client.post(
            "/api/resource/move",
            query_params={
                "from": f"{file.name}",
                "to": "moved.txt"
            },
            extra={"format": "json"}
        )
        assert move_file_response.status_code == 200
        assert move_file_response.data["path"] == ""
        assert move_file_response.data["name"] == "moved.txt"
        assert move_file_response.data["size"] == file.size
        assert move_file_response.data["type"] == ResourceTypes.FILE
