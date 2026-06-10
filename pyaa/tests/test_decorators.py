from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.customer.models import Customer
from pyaa.decorators.customer import customer_required

User = get_user_model()


class CustomerRequiredDecoratorTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.site = Site.objects.get_current()

        @customer_required
        def view(request):
            return HttpResponse(str(request.customer.id))

        self.view = view

    def test_anonymous_user_is_redirected_to_login(self):
        request = self.factory.get("/account")
        request.user = AnonymousUser()

        response = self.view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_user_without_customer_is_redirected_home(self):
        user = User.objects.create_user(
            email="nocustomer@example.com", password="pass", site=self.site
        )
        request = self.factory.get("/account")
        request.user = user

        response = self.view(request)

        self.assertEqual(response.status_code, 302)

    def test_user_with_customer_reaches_view(self):
        user = User.objects.create_user(
            email="customer@example.com", password="pass", site=self.site
        )
        customer = Customer.objects.create(user=user, site=self.site, language_id=1)
        request = self.factory.get("/account")
        request.user = user

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), str(customer.id))
