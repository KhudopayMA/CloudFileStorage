from django.contrib.auth.models import User
from test_plus import APITestCase

# mypy: disable-error-code=misc


class TestSignUpView(APITestCase):
    def test_user_creation(self) -> None:
        data = {"username": "user1", "password": "12345"}
        response = self.post("sign-up", data=data, extra={"format": "json"})
        self.response_201()
        assert response.data["username"] == data["username"]

    def test_exist_user_creation(self) -> None:
        User.objects.create(username="user1", password="12345")
        data = {"username": "user1", "password": "12345"}
        response = self.post("sign-up", data=data, extra={"format": "json"})
        self.response_409()
        assert response.data["message"] == "Username already in use."
