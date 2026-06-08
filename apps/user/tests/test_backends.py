from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

from apps.user.backends import MultiFieldModelBackend

User = get_user_model()


class MultiFieldModelBackendTest(TestCase):
    def setUp(self):
        self.backend = MultiFieldModelBackend()
        self.site = Site.objects.get(pk=settings.SITE_ID)
        self.user = User.objects.create_user(
            email="user@example.com",
            password="secret",
            cpf="52998224725",
            mobile_phone="11987654321",
            site=self.site,
        )

    def test_authenticate_by_email(self):
        result = self.backend.authenticate(
            None, username="user@example.com", password="secret"
        )
        self.assertEqual(result, self.user)

    def test_authenticate_by_cpf(self):
        result = self.backend.authenticate(
            None, username="52998224725", password="secret"
        )
        self.assertEqual(result, self.user)

    def test_authenticate_by_mobile_phone(self):
        result = self.backend.authenticate(
            None, username="11987654321", password="secret"
        )
        self.assertEqual(result, self.user)

    def test_authenticate_with_wrong_password(self):
        result = self.backend.authenticate(
            None, username="user@example.com", password="wrong"
        )
        self.assertIsNone(result)

    def test_authenticate_unknown_user(self):
        result = self.backend.authenticate(
            None, username="missing@example.com", password="secret"
        )
        self.assertIsNone(result)

    def test_authenticate_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        result = self.backend.authenticate(
            None, username="user@example.com", password="secret"
        )
        self.assertIsNone(result)

    @override_settings(SITE_ID=None)
    def test_authenticate_without_site_id(self):
        result = self.backend.authenticate(
            None, username="user@example.com", password="secret"
        )
        self.assertIsNone(result)

    def test_get_user_existing(self):
        self.assertEqual(self.backend.get_user(self.user.pk), self.user)

    def test_get_user_missing(self):
        self.assertIsNone(self.backend.get_user(99999))
