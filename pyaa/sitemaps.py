"""
Sitemap configuration for the Django project.

This module defines sitemap classes for different sections of the website
to help search engines index the content properly.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.content.models import Content, ContentCategory
from apps.gallery.models import Gallery
from apps.shop.models import Plan, Product


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages that don't have associated models.
    """

    priority = 0.8
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return [
            "home",
            "shop_products",
            "contact_index",
            "gallery_index",
        ]

    def location(self, item):
        return reverse(item)


class ContentSitemap(Sitemap):
    """
    Sitemap for content articles.
    """

    priority = 0.7
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Content.objects.filter(active=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("content_by_tag", kwargs={"content_tag": obj.tag})


class ContentCategorySitemap(Sitemap):
    """
    Sitemap for content categories.
    """

    priority = 0.6
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return ContentCategory.objects.all().order_by("name")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("contents_index_view", kwargs={"category_tag": obj.tag})


class GallerySitemap(Sitemap):
    """
    Sitemap for gallery items.
    """

    priority = 0.5
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Gallery.objects.filter(active=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("gallery_by_tag", kwargs={"gallery_tag": obj.tag})


class ProductSitemap(Sitemap):
    """
    Sitemap for shop products.
    """

    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Product.objects.filter(active=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        if obj.slug:
            return reverse(
                "shop_product_details",
                kwargs={"product_token": obj.token, "slug": obj.slug},
            )
        return reverse(
            "shop_product_details_no_slug", kwargs={"product_token": obj.token}
        )


class PlanSitemap(Sitemap):
    """
    Sitemap for subscription plans.
    """

    priority = 0.7
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Plan.objects.filter(active=True).order_by("price")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("shop_plans", kwargs={"plan_type": obj.plan_type})


# dictionary mapping sitemap names to their classes
sitemaps = {
    "static": StaticViewSitemap,
    "content": ContentSitemap,
    "content_categories": ContentCategorySitemap,
    "gallery": GallerySitemap,
    "products": ProductSitemap,
    "plans": PlanSitemap,
}
