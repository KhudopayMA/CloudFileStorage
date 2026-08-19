from django.contrib.auth.models import User
from test_plus import APITestCase

# mypy: disable-error-code=misc


class TestLogoutView(APITestCase):
    def test_user_logout(self) -> None:
        User.objects.create_user(username="user1", password="12345")
        data = {"username": "user1", "password": "12345"}
        self.post("sign-in", data=data, extra={"format": "json"})
        self.response_200()

        self.post("sign-out")
        self.response_204()
