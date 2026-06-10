from django.test import RequestFactory, TestCase

from pyaa.helpers.request import RequestHelper


class RequestHelperTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_next_url_from_get(self):
        request = self.factory.get("/login", {"next": "/dashboard"})
        self.assertEqual(RequestHelper.get_next_url(request), "/dashboard")

    def test_get_next_url_from_post(self):
        request = self.factory.post("/login", {"next": "/account"})
        self.assertEqual(RequestHelper.get_next_url(request), "/account")

    def test_get_next_url_rejects_external_host(self):
        request = self.factory.get("/login", {"next": "https://evil.com/phish"})
        self.assertIsNone(RequestHelper.get_next_url(request))

    def test_get_next_url_missing(self):
        request = self.factory.get("/login")
        self.assertIsNone(RequestHelper.get_next_url(request))
