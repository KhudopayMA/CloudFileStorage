from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestResourceSearchView(TestCase):
    client = APIClient()

    def setUp(self) -> None:
        data = {"username": "user1", "password": "testpassword12345"}
        self.client.post("/api/auth/sign-up", data=data, extra={"format": "json"})
        self.user = User.objects.get(username=data["username"])
        self.client.force_authenticate(user=self.user)

    def test_search_files(self):
        files = []
        files_names = []
        for n in range(3):
            file_name = f"test{n}.txt"
            files_names.append(file_name)
            files.append(
                SimpleUploadedFile(
                    name=file_name,
                    content=b"Test file"
                )
            )
        for file in files:
            self.client.post(
                "/api/resource",
                data={
                    "object": file,
                    "path": ""
                },
                extra={"format": "json"}
            )

        response = self.client.get(
                "/api/resource/search",
                query_params={
                    "query": "test"
                },
                extra={"format": "json"}
            )
        assert response.status_code == 200
        for file in response.data:
            assert file["name"] in files_names



