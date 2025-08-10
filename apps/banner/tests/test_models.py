from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner, BannerAccess
from apps.customer.models import Customer
from apps.language import models as language_models

User = get_user_model()


class BannerModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()

    def test_banner_creation(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

        self.assertTrue(Banner.objects.filter(title="Test Banner").exists())
        self.assertEqual(banner.title, "Test Banner")
        self.assertEqual(banner.zone, BannerZone.HOME)
        self.assertEqual(banner.sort_order, 1)
        self.assertTrue(banner.active)

    def test_banner_deletion(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

        banner.delete()

        self.assertFalse(Banner.objects.filter(title="Test Banner").exists())

    def test_get_banner(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

        fetched_banner = Banner.objects.get(title="Test Banner")

        self.assertEqual(fetched_banner.title, "Test Banner")
        self.assertEqual(fetched_banner.zone, BannerZone.HOME)

    def test_get_nonexistent_banner(self):
        with self.assertRaises(ObjectDoesNotExist):
            Banner.objects.get(title="Nonexistent Banner")

    def test_banner_str(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

        self.assertEqual(str(banner), "Test Banner")

    def test_banner_default_values(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
        )

        self.assertTrue(banner.active)
        self.assertEqual(banner.sort_order, 0)
        self.assertFalse(banner.target_blank)
        self.assertIsNotNone(banner.token)
        self.assertIsNotNone(banner.created_at)
        self.assertIsNotNone(banner.updated_at)

    def test_banner_with_link_and_target(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            link="https://example.com",
            target_blank=True,
            zone=BannerZone.SIGNIN,
            sort_order=2,
        )

        self.assertEqual(banner.link, "https://example.com")
        self.assertTrue(banner.target_blank)
        self.assertEqual(banner.zone, BannerZone.SIGNIN)

    def test_banner_with_datetime_fields(self):
        start_at = timezone.now()
        end_at = start_at + timedelta(days=30)

        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.SIGNUP,
            start_at=start_at,
            end_at=end_at,
        )

        self.assertEqual(banner.start_at, start_at)
        self.assertEqual(banner.end_at, end_at)

    def test_banner_zone_choices(self):
        banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
        )

        self.assertIn(banner.zone, [choice[0] for choice in BannerZone.choices])

    def test_banner_optional_fields(self):
        banner = Banner.objects.create(
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
        )

        self.assertIsNone(banner.site)
        self.assertIsNone(banner.language)
        self.assertIsNone(banner.link)
        self.assertIsNone(banner.start_at)
        self.assertIsNone(banner.end_at)


class BannerAccessModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="test_image.jpg",
            zone=BannerZone.HOME,
        )
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        self.customer = Customer.objects.create(
            user=self.user,
            site=self.site,
            language=self.language,
        )

    def test_banner_access_creation(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            customer=self.customer,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="BR",
        )

        self.assertTrue(BannerAccess.objects.filter(banner=self.banner).exists())
        self.assertEqual(access.access_type, BannerAccessType.VIEW)
        self.assertEqual(access.ip_address, "192.168.1.1")
        self.assertEqual(access.country_code, "BR")

    def test_banner_access_deletion(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            customer=self.customer,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="BR",
        )

        access.delete()

        self.assertFalse(BannerAccess.objects.filter(banner=self.banner).exists())

    def test_get_banner_access(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            customer=self.customer,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="BR",
        )

        fetched_access = BannerAccess.objects.get(banner=self.banner)

        self.assertEqual(fetched_access.access_type, BannerAccessType.VIEW)
        self.assertEqual(fetched_access.ip_address, "192.168.1.1")

    def test_get_nonexistent_banner_access(self):
        with self.assertRaises(ObjectDoesNotExist):
            BannerAccess.objects.get(banner_id=99999)

    def test_banner_access_str(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            customer=self.customer,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="BR",
        )

        str_repr = str(access)
        self.assertIn("Test Banner", str_repr)
        self.assertIn("view", str_repr)
        self.assertIn("192.168.1.1", str_repr)

    def test_banner_access_without_customer(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            access_type=BannerAccessType.CLICK,
            ip_address="192.168.1.1",
            country_code="US",
        )

        self.assertIsNone(access.customer)
        self.assertEqual(access.access_type, BannerAccessType.CLICK)

    def test_banner_access_type_choices(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
        )

        self.assertIn(
            access.access_type, [choice[0] for choice in BannerAccessType.choices]
        )

    def test_banner_access_get_ip_address_ipv4(self):
        """Test IPv4 address handling"""
        # Test common IPv4 addresses
        test_ips = ["192.168.1.1", "10.0.0.1", "127.0.0.1", "8.8.8.8"]

        for ip_string in test_ips:
            with self.subTest(ip_string=ip_string):
                # Create banner access with the IP address
                access = BannerAccess.objects.create(
                    banner=self.banner,
                    access_type=BannerAccessType.VIEW,
                    ip_address=ip_string,
                )

                # Verify our conversion matches the original
                self.assertEqual(access.get_ip_address(), ip_string)

    def test_banner_access_get_ip_address_ipv6(self):
        """Test IPv6 address handling"""
        # Test common IPv6 addresses
        test_ips = ["2001:db8::1", "::1", "fe80::1"]

        for ip_string in test_ips:
            with self.subTest(ip_string=ip_string):
                # Create banner access with the IP address
                access = BannerAccess.objects.create(
                    banner=self.banner,
                    access_type=BannerAccessType.VIEW,
                    ip_address=ip_string,
                )

                # Verify our conversion matches the original
                self.assertEqual(access.get_ip_address(), ip_string)

    def test_banner_access_country_code_uppercase(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="br",
        )

        # The clean method should convert to uppercase
        access.clean()
        self.assertEqual(access.country_code, "BR")

    def test_banner_access_country_code_none(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
        )

        # Should not raise error when country_code is none
        access.clean()
        self.assertIsNone(access.country_code)

    def test_banner_access_save_calls_clean(self):
        access = BannerAccess(
            banner=self.banner,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
            country_code="br",
        )

        # Save should call clean and convert country_code to uppercase
        access.save()
        self.assertEqual(access.country_code, "BR")

    def test_banner_access_related_names(self):
        access = BannerAccess.objects.create(
            banner=self.banner,
            customer=self.customer,
            access_type=BannerAccessType.VIEW,
            ip_address="192.168.1.1",
        )

        # Test related names
        self.assertIn(access, self.banner.accesses.all())
        self.assertIn(access, self.customer.banner_accesses.all())

    def test_banner_access_required_fields(self):
        # Should not be able to create without required fields
        with self.assertRaises(Exception):
            BannerAccess.objects.create(
                banner=self.banner,
                # Missing access_type and ip_address
            )

    def test_banner_access_ip_edge_cases(self):
        """Test edge cases for IP addresses"""
        # Test edge cases
        edge_cases = [
            "0.0.0.0",  # Unspecified address
            "255.255.255.255",  # Broadcast address
            "::",  # Unspecified IPv6
            "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",  # Max IPv6
        ]

        for ip_string in edge_cases:
            with self.subTest(ip_string=ip_string):
                access = BannerAccess.objects.create(
                    banner=self.banner,
                    access_type=BannerAccessType.VIEW,
                    ip_address=ip_string,
                )

                self.assertEqual(access.get_ip_address(), ip_string)
