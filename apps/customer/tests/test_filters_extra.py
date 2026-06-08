from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.customer.filters import (
    CpfFilter,
    MobilePhoneFilter,
    SiteFilter,
)
from apps.customer.models import Customer

User = get_user_model()


class MockModelAdmin(ModelAdmin):
    pass


class CustomerFiltersExtraTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/admin")
        self.model_admin = MockModelAdmin(Customer, admin_site=None)
        self.site = Site.objects.get_current()

        self.user = User.objects.create_user(
            email="filt@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            cpf="52998224725",
            mobile_phone="11999999999",
            site=self.site,
        )
        self.customer = Customer.objects.create(
            user=self.user,
            site=self.site,
            language_id=1,
            gender="male",
        )

    def test_cpf_filter_with_value(self):
        flt = CpfFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: "52998224725"
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertTrue(result.filter(pk=self.customer.pk).exists())

    def test_cpf_filter_without_value(self):
        flt = CpfFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: None
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertEqual(result.count(), Customer.objects.count())

    def test_mobile_phone_filter_with_value(self):
        flt = MobilePhoneFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: "11999999999"
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertTrue(result.filter(pk=self.customer.pk).exists())

    def test_mobile_phone_filter_without_value(self):
        flt = MobilePhoneFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: None
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertEqual(result.count(), Customer.objects.count())

    def test_site_filter_lookups(self):
        flt = SiteFilter(self.request, {}, Customer, self.model_admin)
        lookups = flt.lookups(self.request, self.model_admin)
        site_ids = [item[0] for item in lookups]
        self.assertIn(str(self.site.id), site_ids)

    def test_site_filter_with_value(self):
        flt = SiteFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: str(self.site.id)
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertTrue(result.filter(pk=self.customer.pk).exists())

    def test_site_filter_without_value(self):
        flt = SiteFilter(self.request, {}, Customer, self.model_admin)
        flt.value = lambda: None
        result = flt.queryset(self.request, Customer.objects.all())
        self.assertEqual(result.count(), Customer.objects.count())
