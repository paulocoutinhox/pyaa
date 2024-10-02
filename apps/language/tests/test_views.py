from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LanguageAPITest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        # initialize the API client
        self.client = APIClient()

        # generate a token for the test user
        refresh = RefreshToken.for_user(self.user)

        # set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # add necessary permissions to the user
        permission = Permission.objects.get(codename="view_language")
        self.user.user_permissions.add(permission)
        self.user.save()

    def test_get_languages(self):
        # get languages
        url = reverse("language")
        response = self.client.get(url)

        # tests
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        languages = [language["name"] for language in response.data["results"]]
        self.assertIn("Spanish", languages)
        self.assertIn("Portuguese", languages)
        self.assertIn("English", languages)
