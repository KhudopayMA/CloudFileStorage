from test_plus import APITestCase

from test.factories import UserFactory

# mypy: ignore-errors



class TestLogoutView(APITestCase):
    def setUp(self) -> None:
        self.password = "testpassword12345"
        self.user = UserFactory(password=self.password)

    def test_user_logout(self) -> None:
        data = {"username": self.user.username, "password": self.password}
        self.post("sign-in", data=data, extra={"format": "json"})
        self.response_200()

        self.post("sign-out")
        self.response_204()

        self.get("user-me", extra={"format": "json"})
        self.response_403()
