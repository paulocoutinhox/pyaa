from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from django.utils.translation import override

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.helpers import BannerHelper
from apps.banner.models import Banner, BannerAccess
from apps.customer.models import Customer
from apps.language import models as language_models

User = get_user_model()


class BannerHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.factory = RequestFactory()

        # create test banners
        self.banner_home = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Home Banner",
            image="home_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

        self.banner_signin = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Signin Banner",
            image="signin_banner.jpg",
            zone=BannerZone.SIGNIN,
            sort_order=2,
            active=True,
        )

        # create inactive banner
        self.inactive_banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Inactive Banner",
            image="inactive_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=3,
            active=False,
        )

        # create banner with date restrictions
        self.future_banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Future Banner",
            image="future_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=4,
            active=True,
            start_at=timezone.now() + timedelta(days=1),
        )

        self.expired_banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Expired Banner",
            image="expired_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=0,
            active=True,
            end_at=timezone.now() - timedelta(days=1),
        )

        # create banner without site (global)
        self.global_banner = Banner.objects.create(
            site=None,
            language=self.language,
            title="Global Banner",
            image="global_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=6,
            active=True,
        )

        # create banner without language (language-agnostic)
        self.language_agnostic_banner = Banner.objects.create(
            site=self.site,
            language=None,
            title="Language Agnostic Banner",
            image="lang_agnostic_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=7,
            active=True,
        )

    def tearDown(self):
        cache.clear()

    def test_get_banners_basic(self):
        # test basic banner retrieval
        banners = BannerHelper.get_banners(BannerZone.HOME)

        # should return 3 active banners: home, global, language_agnostic
        # expired_banner should not be returned due to end_at date
        self.assertEqual(len(banners), 3)
        self.assertIn(self.banner_home, banners)
        self.assertIn(self.global_banner, banners)
        self.assertIn(self.language_agnostic_banner, banners)
        self.assertNotIn(self.expired_banner, banners)
        self.assertNotIn(self.inactive_banner, banners)
        self.assertNotIn(self.future_banner, banners)

    def test_get_banners_with_language(self):
        # test getting banners with specific language
        with override("en"):
            banners = BannerHelper.get_banners(BannerZone.HOME, language="en")
            self.assertEqual(len(banners), 3)

    def test_get_banners_ordering(self):
        # test that banners are returned in correct sort order
        banners = list(BannerHelper.get_banners(BannerZone.HOME))
        self.assertEqual(banners[0].sort_order, 1)  # banner_home
        self.assertEqual(banners[1].sort_order, 6)  # global_banner
        self.assertEqual(banners[2].sort_order, 7)  # language_agnostic_banner

    def test_get_banners_cache(self):
        # test that banners are cached
        with patch("apps.banner.helpers.cache.get") as mock_cache_get:
            mock_cache_get.return_value = [self.banner_home]
            banners = BannerHelper.get_banners(BannerZone.HOME)
            self.assertEqual(banners, [self.banner_home])

    def test_get_banner_by_token(self):
        # test getting banner by token
        banner = BannerHelper.get_banner_by_token(self.banner_home.token)
        self.assertEqual(banner, self.banner_home)

    def test_get_banner_by_token_not_found(self):
        # test getting banner by non-existent token
        fake_token = uuid4()
        banner = BannerHelper.get_banner_by_token(fake_token)
        self.assertIsNone(banner)

    def test_get_banner_by_token_inactive(self):
        # test that inactive banners are not returned by token
        self.banner_home.active = False
        self.banner_home.save()

        banner = BannerHelper.get_banner_by_token(self.banner_home.token)
        self.assertIsNone(banner)

    @override_settings(BANNER_ACCESS_INTERVAL=3600)
    def test_track_banner_access_success(self):
        # test successful banner access tracking
        request = self.factory.get("/")
        request.META = {"REMOTE_ADDR": "192.168.1.1"}
        request.user = Mock()
        request.user.is_authenticated = False

        result = BannerHelper.track_banner_access(
            request, self.banner_home, BannerAccessType.VIEW
        )

        self.assertTrue(result)

        # check that access record was created
        access = BannerAccess.objects.get(banner=self.banner_home)
        self.assertEqual(access.ip_address, "192.168.1.1")
        self.assertEqual(access.access_type, BannerAccessType.VIEW)
        self.assertIsNone(access.customer)

    @override_settings(BANNER_ACCESS_INTERVAL=3600)
    def test_track_banner_access_with_customer(self):
        # test banner access tracking with authenticated customer
        user = User.objects.create_user(
            username="testuser",
            password="testpass",
            email="test@example.com",  # required field
        )
        customer = Customer.objects.create(
            user=user, site=self.site, language=self.language
        )

        request = self.factory.get("/")
        request.META = {"REMOTE_ADDR": "192.168.1.1"}
        request.user = user

        # mock the has_customer method and customer attribute
        with patch.object(user, "has_customer", return_value=True):
            user.customer = customer
            result = BannerHelper.track_banner_access(
                request, self.banner_home, BannerAccessType.CLICK
            )

        self.assertTrue(result)

        # check that access record was created with customer
        access = BannerAccess.objects.get(banner=self.banner_home)
        self.assertEqual(access.customer, customer)
        self.assertEqual(access.access_type, BannerAccessType.CLICK)

    @override_settings(BANNER_ACCESS_INTERVAL=3600)
    def test_track_banner_access_interval_check(self):
        # test that banner access respects interval checking
        request = self.factory.get("/")
        request.META = {"REMOTE_ADDR": "192.168.1.1"}
        request.user = Mock()
        request.user.is_authenticated = False

        # first access should succeed
        result1 = BannerHelper.track_banner_access(
            request, self.banner_home, BannerAccessType.VIEW
        )
        self.assertTrue(result1)

        # second access within interval should fail
        result2 = BannerHelper.track_banner_access(
            request, self.banner_home, BannerAccessType.VIEW
        )
        self.assertFalse(result2)

        # should only have one access record
        access_count = BannerAccess.objects.filter(
            banner=self.banner_home,
            ip_address="192.168.1.1",
            access_type=BannerAccessType.VIEW,
        ).count()
        self.assertEqual(access_count, 1)

    def test_track_banner_access_no_ip(self):
        # test banner access tracking when no IP address is available
        request = self.factory.get("/")
        request.META = {}
        request.user = Mock()
        request.user.is_authenticated = False

        result = BannerHelper.track_banner_access(
            request, self.banner_home, BannerAccessType.VIEW
        )

        self.assertFalse(result)

        # no access record should be created
        access_count = BannerAccess.objects.filter(banner=self.banner_home).count()
        self.assertEqual(access_count, 0)

    def test_track_banner_access_invalid_ip(self):
        # test banner access tracking with invalid IP address
        request = self.factory.get("/")
        request.META = {"REMOTE_ADDR": "invalid_ip"}
        request.user = Mock()
        request.user.is_authenticated = False

        result = BannerHelper.track_banner_access(
            request, self.banner_home, BannerAccessType.VIEW
        )

        self.assertFalse(result)

        # no access record should be created
        access_count = BannerAccess.objects.filter(banner=self.banner_home).count()
        self.assertEqual(access_count, 0)
