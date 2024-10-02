from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UserAPITest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        # initialize the api client
        self.client = APIClient()

    def test_login(self):
        # login to get access and refresh tokens
        url = "/api/token/"
        data = {"email": "testuser@example.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        # first, login to get the refresh token
        login_url = "/api/token/"
        login_data = {"email": "testuser@example.com", "password": "testpassword"}
        login_response = self.client.post(login_url, login_data, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        refresh_token = login_response.data["refresh"]

        # now, use the refresh token to get a new access token
        refresh_url = "/api/token/refresh/"
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_login_invalid_credentials(self):
        url = "/api/token/"
        data = {"email": "wronguser@example.com", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_token_refresh_invalid_token(self):
        refresh_url = "/api/token/refresh/"
        refresh_data = {"refresh": "invalidtoken"}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", refresh_response.data)
