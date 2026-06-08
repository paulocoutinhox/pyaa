from decimal import Decimal

from django.contrib.sites.models import Site
from django.test import TestCase

from apps.content.models import Content, ContentCategory
from apps.gallery.models import Gallery
from apps.language import models as language_models
from apps.shop.enums import PaymentGateway, PlanType
from apps.shop.models import Plan, Product
from pyaa.sitemaps import (
    ContentCategorySitemap,
    ContentSitemap,
    GallerySitemap,
    PlanSitemap,
    ProductSitemap,
    StaticViewSitemap,
    sitemaps,
)


class StaticViewSitemapTest(TestCase):
    def test_items_and_location(self):
        sitemap = StaticViewSitemap()
        items = sitemap.items()

        self.assertEqual(
            items, ["home", "shop_products", "contact_index", "gallery_index"]
        )

        for item in items:
            self.assertTrue(sitemap.location(item).startswith("/"))


class ContentSitemapTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.active = Content.objects.create(
            site=self.site,
            language=self.language,
            title="Active Content",
            tag="active-content",
            active=True,
        )
        self.inactive = Content.objects.create(
            site=self.site,
            language=self.language,
            title="Inactive Content",
            tag="inactive-content",
            active=False,
        )

    def test_items_only_returns_active(self):
        sitemap = ContentSitemap()
        items = list(sitemap.items())

        self.assertIn(self.active, items)
        self.assertNotIn(self.inactive, items)

    def test_lastmod_returns_updated_at(self):
        sitemap = ContentSitemap()
        self.assertEqual(sitemap.lastmod(self.active), self.active.updated_at)

    def test_location_uses_content_tag(self):
        sitemap = ContentSitemap()
        self.assertIn(self.active.tag, sitemap.location(self.active))


class ContentCategorySitemapTest(TestCase):
    def setUp(self):
        self.category = ContentCategory.objects.create(name="News", tag="news")

    def test_items_returns_all_categories(self):
        sitemap = ContentCategorySitemap()
        self.assertIn(self.category, list(sitemap.items()))

    def test_lastmod_returns_updated_at(self):
        sitemap = ContentCategorySitemap()
        self.assertEqual(sitemap.lastmod(self.category), self.category.updated_at)

    def test_location_uses_category_tag(self):
        sitemap = ContentCategorySitemap()
        self.assertIn(self.category.tag, sitemap.location(self.category))


class GallerySitemapTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.active = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="Active Gallery",
            tag="active-gallery",
            active=True,
        )
        self.inactive = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="Inactive Gallery",
            tag="inactive-gallery",
            active=False,
        )

    def test_items_only_returns_active(self):
        sitemap = GallerySitemap()
        items = list(sitemap.items())

        self.assertIn(self.active, items)
        self.assertNotIn(self.inactive, items)

    def test_lastmod_returns_updated_at(self):
        sitemap = GallerySitemap()
        self.assertEqual(sitemap.lastmod(self.active), self.active.updated_at)

    def test_location_uses_gallery_tag(self):
        sitemap = GallerySitemap()
        self.assertIn(self.active.tag, sitemap.location(self.active))


class ProductSitemapTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        self.with_slug = Product.objects.create(
            site=self.site,
            name="Product One",
            currency="USD",
            price=Decimal("10.00"),
            active=True,
        )
        self.no_slug = Product.objects.create(
            site=self.site,
            name="Product Two",
            currency="USD",
            price=Decimal("20.00"),
            active=True,
        )
        # force slug to empty to exercise the no-slug branch
        Product.objects.filter(pk=self.no_slug.pk).update(slug="")
        self.no_slug.refresh_from_db()
        self.inactive = Product.objects.create(
            site=self.site,
            name="Product Inactive",
            currency="USD",
            price=Decimal("5.00"),
            active=False,
        )

    def test_items_only_returns_active(self):
        sitemap = ProductSitemap()
        items = list(sitemap.items())

        self.assertIn(self.with_slug, items)
        self.assertNotIn(self.inactive, items)

    def test_lastmod_returns_updated_at(self):
        sitemap = ProductSitemap()
        self.assertEqual(sitemap.lastmod(self.with_slug), self.with_slug.updated_at)

    def test_location_with_slug(self):
        sitemap = ProductSitemap()
        location = sitemap.location(self.with_slug)
        self.assertIn(str(self.with_slug.token), location)
        self.assertIn(self.with_slug.slug, location)

    def test_location_without_slug(self):
        sitemap = ProductSitemap()
        location = sitemap.location(self.no_slug)
        self.assertIn(str(self.no_slug.token), location)


class PlanSitemapTest(TestCase):
    def setUp(self):
        self.active = Plan.objects.create(
            name="Active Plan",
            plan_type=PlanType.SUBSCRIPTION,
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=Decimal("9.99"),
            active=True,
        )
        self.inactive = Plan.objects.create(
            name="Inactive Plan",
            plan_type=PlanType.SUBSCRIPTION,
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=Decimal("1.99"),
            active=False,
        )

    def test_items_only_returns_active(self):
        sitemap = PlanSitemap()
        items = list(sitemap.items())

        self.assertIn(self.active, items)
        self.assertNotIn(self.inactive, items)

    def test_lastmod_returns_updated_at(self):
        sitemap = PlanSitemap()
        self.assertEqual(sitemap.lastmod(self.active), self.active.updated_at)

    def test_location_uses_plan_type(self):
        sitemap = PlanSitemap()
        location = sitemap.location(self.active)
        self.assertIn(self.active.plan_type, location)


class SitemapsRegistryTest(TestCase):
    def test_registry_contains_all_sitemaps(self):
        self.assertEqual(
            set(sitemaps.keys()),
            {
                "static",
                "content",
                "content_categories",
                "gallery",
                "products",
                "plans",
            },
        )
