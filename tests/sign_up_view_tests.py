import pytest
from test_plus.test import TestCase
from rest_framework.test import APIClient

class SignUpViewTests(TestCase):
    client_class = APIClient

    def test_post(self):



