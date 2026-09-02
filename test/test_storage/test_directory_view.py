from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from test_plus import APITestCase
from rest_framework.test import force_authenticate, APIClient

from storage.enums import ResourceTypes
from test.factories import UserFactory


@pytest.mark.django_db
class TestDirectoryView(TestCase):
    client = APIClient()

    def setUp(self) -> None:
        data = {"username": "user1", "password": "testpassword12345"}
        self.client.post("/api/auth/sign-up", data=data, extra={"format": "json"})
        self.user = User.objects.get(username=data["username"])
        self.client.force_authenticate(user=self.user)

    def test_create_directory(self) -> None:
        create_dir_response = self.client.post(
            "/api/directory",
            query_params={"path": "test/"},
            extra={"format": "json"}
        )
        assert create_dir_response.status_code == 201
        get_dir_content_response = self.client.get(
            "/api/directory",
            query_params={"path": ""},
            extra={"format": "json"}
        )
        assert get_dir_content_response.status_code == 200
        child_dir_meta = get_dir_content_response.data[0]
        assert child_dir_meta["path"] == ""
        assert child_dir_meta["name"] == "test/"
        assert child_dir_meta["type"] == ResourceTypes.DIRECTORY

    def test_directory_already_exists(self) -> None:
        self.client.post(
            "/api/directory",
            query_params={"path": "test/"},
            extra={"format": "json"}
        )
        response = self.client.post(
            "/api/directory",
            query_params={"path": "test/"},
            extra={"format": "json"}
        )
        assert response.status_code == 409
        assert response.data["message"] == "Directory already exists."

    def test_create_dir_with_non_existent_path(self) -> None:
        response = self.client.post(
            "/api/directory",
            query_params={"path": "non_existent/test/"},
            extra={"format": "json"}
        )
        assert response.status_code == 404
        assert response.data["message"] == "Parent directory not found."
