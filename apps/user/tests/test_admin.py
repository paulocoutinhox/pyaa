from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.user.admin import UserAdmin

User = get_user_model()


class MockRequest:
    path = "/admin"


class MockRequestAutoComplete:
    path = "/admin/autocomplete"


class UserAdminTest(TestCase):
    def setUp(self):
        self.site_obj = Site.objects.create(name="Test Site", domain="test.com")
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            cpf="52998224725",
            mobile_phone="11987654321",
            site=self.site_obj,
        )
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = UserAdmin(User, self.admin_site)
        self.request = self.factory.get("/admin")

    def test_get_queryset(self):
        request = MockRequest()
        queryset = self.admin.get_queryset(request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user)

    def test_get_search_results(self):
        request = MockRequest()
        queryset = User.objects.all()
        search_term = "Test"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)
        self.assertEqual(queryset.first(), self.user)

    def test_get_search_results_by_email(self):
        request = MockRequest()
        queryset = User.objects.all()
        search_term = "test@example.com"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)
        self.assertEqual(queryset.first(), self.user)

    def test_get_search_results_by_cpf(self):
        request = MockRequest()
        queryset = User.objects.all()
        search_term = "52998224725"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)
        self.assertEqual(queryset.first(), self.user)
