from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.utils.translation import get_language

from apps.gallery.models import Gallery


class GalleryHelper:
    @staticmethod
    def get_gallery(gallery_id=None, gallery_tag=None, site_id=None):
        # get current site
        if site_id is None:
            current_site = Site.objects.get_current()
            site_id = current_site.id

        # create cache key based on parameters
        cache_key = None

        if gallery_id:
            cache_key = f"gallery-by-id-{gallery_id}-{site_id}"
        elif gallery_tag:
            user_language = get_language()

            if user_language:
                user_language = user_language.lower()
            cache_key = f"gallery-by-tag-{gallery_tag}-{user_language}-{site_id}"

        # try to get from cache first
        if cache_key:
            cached_gallery = cache.get(cache_key)

            if cached_gallery is not None:
                return cached_gallery

        filter_kwargs = {"active": True}

        # site filtering
        site_filter = models.Q(site_id=site_id) | models.Q(site__isnull=True)

        # if gallery_id is provided, ignore language and return the gallery directly
        if gallery_id:
            filter_kwargs["id"] = gallery_id

            gallery = (
                Gallery.objects.filter(**filter_kwargs)
                .filter(site_filter)
                .prefetch_related("gallery_photos")
                .first()
            )

            if gallery:
                # cache for 1 hour
                cache.set(cache_key, gallery, timeout=3600)

            return gallery

        # if gallery_tag is provided, apply language priority logic (check both code_iso_639_1 and code_iso_language)
        elif gallery_tag:
            user_language = get_language()

            if user_language:
                user_language = user_language.lower()

            filter_kwargs["tag"] = gallery_tag

            # filter gallery based on language priority (user's language, then en-us, then global galleries)
            gallery = (
                Gallery.objects.filter(**filter_kwargs)
                .filter(site_filter)
                .prefetch_related("gallery_photos")
                .order_by(
                    models.Case(
                        # give priority to galleries in the user's language, checking both code_iso_639_1 and code_iso_language
                        models.When(
                            models.Q(language__code_iso_language=user_language)
                            | models.Q(language__code_iso_639_1=user_language),
                            then=0,
                        ),
                        # fallback to 'en-us' by checking both code_iso_639_1 and code_iso_language
                        models.When(
                            models.Q(language__code_iso_language="en-us")
                            | models.Q(language__code_iso_639_1="en"),
                            then=1,
                        ),
                        # lastly, consider global galleries (language=None)
                        models.When(language__isnull=True, then=2),
                        # default to the highest number if no match is found
                        default=models.Value(3),
                        output_field=models.IntegerField(),
                    )
                )
                .first()
            )

            if gallery:
                # cache for 1 hour
                cache.set(cache_key, gallery, timeout=3600)

            return gallery
        else:
            raise ValueError("gallery_id or gallery_tag must be provided.")

    @staticmethod
    def get_gallery_list(site_id=None):
        # get current site if not provided
        if site_id is None:
            current_site = Site.objects.get_current()
            site_id = current_site.id

        user_language = get_language()

        if user_language:
            user_language = user_language.lower()

        # site filtering
        site_filter = models.Q(site_id=site_id) | models.Q(site__isnull=True)

        # only include galleries in the user's language or global (language=None)
        return (
            Gallery.objects.filter(
                models.Q(language__code_iso_639_1=user_language)
                | models.Q(language__code_iso_language=user_language)
                | models.Q(language__isnull=True),
                active=True,
            )
            .filter(site_filter)
            .prefetch_related("gallery_photos")
            .order_by("-id")
        )
