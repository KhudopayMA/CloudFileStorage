from test_plus import APITestCase

from test.factories import UserFactory

# mypy: ignore-errors


class TestSignInView(APITestCase):
    def setUp(self) -> None:
        self.password = "testpassword12345"
        self.user = UserFactory(password=self.password)

    def test_user_login(self) -> None:
        data = {"username": self.user.username, "password": self.password}
        response = self.post("sign-in", data=data, extra={"format": "json"})
        self.response_200()
        assert response.data["username"] == data["username"]
        me_response = self.get("user-me", extra={"format": "json"})
        self.response_200()
        assert me_response.data["username"] == data["username"]

    def test_login_with_wrong_credentials(self) -> None:
        data = {"username": "wrongname", "password": "wrongpassword12345"}
        response = self.post("sign-in", data=data, extra={"format": "json"})
        self.response_401()
        assert response.data["message"] == "Wrong username or password"
