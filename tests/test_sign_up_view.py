from test_plus.test import APITestCase


class SignUpViewTests(APITestCase):

    def test_post(self):
        data = {"username": "user1", "password": "12345"}
        self.post("api/auth/sign-up", data=data, extra={"format": "json"})
        self.response_200()
        self.assertResponseMessages("user1")
