from django.contrib.auth.models import User
from test_plus import APITestCase

from test.factories import UserFactory


# mypy: disable-error-code=misc


class TestSignUpView(APITestCase):
    def setUp(self) -> None:
        self.password = "testpassword12345"
        self.user = UserFactory(password=self.password)

    def test_user_creation(self) -> None:
        data = {"username": "user1", "password": "testpassword12345"}
        response = self.post("sign-up", data=data, extra={"format": "json"})
        self.response_201()
        assert response.data["username"] == data["username"]

    def test_exist_user_creation(self) -> None:
        data = {"username": self.user.username, "password": self.password}
        response = self.post("sign-up", data=data, extra={"format": "json"})
        self.response_409()
        assert response.data["message"] == "Username already in use."
