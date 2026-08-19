from django.contrib.auth.models import User
from test_plus import APITestCase

# mypy: disable-error-code=misc


class TestSignInView(APITestCase):
    def test_user_login(self) -> None:
        User.objects.create_user(username="user1", password="12345")
        data = {"username": "user1", "password": "12345"}
        response = self.post("sign-in", data=data, extra={"format": "json"})
        self.response_200()
        assert response.data["username"] == data["username"]

    def test_login_with_wrong_credentials(self) -> None:
        User.objects.create_user(username="user1", password="12345")
        data = {"username": "user2", "password": "12345"}
        response = self.post("sign-in", data=data, extra={"format": "json"})
        self.response_401()
        assert response.data["message"] == "Wrong username or password"
