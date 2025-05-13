from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import get_language
from ipware import get_client_ip

from apps.banner.models import Banner, BannerAccess


class BannerHelper:
    @staticmethod
    def get_banners(zone, language=None, site_id=None):
        # get current language if not provided
        if not language:
            language = get_language()
            if language:
                language = language.lower()

        # get current site if not provided
        if site_id is None:
            site_id = settings.SITE_ID

        # create cache key based on parameters
        cache_key = f"banners-{zone}-{site_id}-{language}"

        # try to get from cache first
        cached_banners = cache.get(cache_key)
        if cached_banners is not None:
            return cached_banners

        # get current datetime for date filtering
        now = timezone.now()

        # define filter criteria
        filter_kwargs = {
            "active": True,
            "zone": zone,
        }

        # add date range conditions
        date_filter = Q(start_at__isnull=True) | Q(start_at__lte=now)
        date_filter &= Q(end_at__isnull=True) | Q(end_at__gte=now)

        # add site and language conditions
        site_filter = Q(site_id=site_id) | Q(site__isnull=True)
        language_filter = (
            Q(language__code_iso_language=language)
            | Q(language__code_iso_639_1=language)
            | Q(language__isnull=True)
        )

        # get banners with all conditions
        banners = (
            Banner.objects.filter(**filter_kwargs)
            .filter(date_filter)
            .filter(site_filter)
            .filter(language_filter)
            .order_by("sort_order")
            .select_related("language", "site")
        )

        # cache for 1 hour
        cache.set(cache_key, banners, timeout=3600)

        return banners

    @staticmethod
    def get_banner_by_token(token):
        # create cache key
        cache_key = f"banner-token-{token}"

        # try to get from cache first
        cached_banner = cache.get(cache_key)
        if cached_banner is not None:
            return cached_banner

        # get current datetime for date filtering
        now = timezone.now()

        # get banner with date range conditions
        date_filter = Q(start_at__isnull=True) | Q(start_at__lte=now)
        date_filter &= Q(end_at__isnull=True) | Q(end_at__gte=now)

        banner = (
            Banner.objects.filter(token=token, active=True)
            .filter(date_filter)
            .select_related("language", "site")
            .first()
        )

        if banner:
            # cache for 1 hour
            cache.set(cache_key, banner, timeout=3600)

        return banner

    @staticmethod
    def track_banner_access(request, banner, access_type):
        """
        Track banner access with IP-based interval checking and customer tracking.
        Returns True if access was tracked, False if skipped due to interval check.

        :param request: The HTTP request object
        :param banner: The Banner object being accessed
        :param access_type: BannerAccessType (VIEW or CLICK)
        :return: bool indicating if access was tracked
        """
        # get client ip
        client_ip, _ = get_client_ip(request)
        if not client_ip:
            return False

        # convert ip to integer for storage
        ip_parts = client_ip.split(".")
        ip_number = sum(
            int(part) << (8 * i) for i, part in enumerate(reversed(ip_parts))
        )

        # get customer if logged in
        customer = None
        if request.user.is_authenticated and request.user.has_customer():
            customer = request.user.customer

        # calculate interval window
        now = timezone.now()
        interval_start = now - timezone.timedelta(
            seconds=settings.BANNER_ACCESS_INTERVAL
        )

        # check if there's any access within the interval for this type
        has_recent_access = BannerAccess.objects.filter(
            banner=banner,
            ip_number=ip_number,
            access_type=access_type,
            created_at__gte=interval_start,
        ).exists()

        if has_recent_access:
            return False

        # get country code from cloudflare header
        country_code = request.META.get("HTTP_CF_IPCOUNTRY", "").upper()

        if not country_code or len(country_code) != 2:
            country_code = None

        # create access record
        BannerAccess.objects.create(
            banner=banner,
            ip_number=ip_number,
            customer=customer,
            access_type=access_type,
            country_code=country_code,
            created_at=now,
        )

        return True
