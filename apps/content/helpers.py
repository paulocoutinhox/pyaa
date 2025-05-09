from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.utils.translation import get_language

from apps.content.models import Content


class ContentHelper:
    @staticmethod
    def get_content(content_id=None, content_tag=None, site_id=None):
        # get current site
        if site_id is None:
            current_site = Site.objects.get_current()
            site_id = current_site.id

        # create cache key based on parameters
        cache_key = None

        if content_id:
            cache_key = f"content-by-id-{content_id}-{site_id}"
        elif content_tag:
            user_language = get_language()

            if user_language:
                user_language = user_language.lower()
            cache_key = f"content-by-tag-{content_tag}-{user_language}-{site_id}"

        # try to get from cache first
        if cache_key:
            cached_content = cache.get(cache_key)

            if cached_content is not None:
                return cached_content

        # define filter criteria based on passed parameters (id or tag)
        filter_kwargs = {"active": True}

        # site filtering
        site_filter = models.Q(site_id=site_id) | models.Q(site__isnull=True)

        # if content_id is provided, ignore language and return the content directly
        if content_id:
            filter_kwargs["id"] = content_id
            content = (
                Content.objects.filter(**filter_kwargs).filter(site_filter).first()
            )

            if content:
                # cache for 1 hour
                cache.set(cache_key, content, timeout=3600)

            return content

        # if content_tag is provided, apply language priority logic
        elif content_tag:
            # get browser's language
            user_language = get_language()

            if user_language:
                user_language = user_language.lower()

            filter_kwargs["tag"] = content_tag

            # filter content based on language priority (user's language, then en-us, then any language)
            content = (
                Content.objects.filter(**filter_kwargs)
                .filter(site_filter)
                .order_by(
                    models.Case(
                        # check both code_iso_639_1 and code_iso_language for the user's language
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
                        # lastly, consider global content (language=None)
                        models.When(language__isnull=True, then=2),
                        # default to the highest number if no match is found
                        default=models.Value(3),
                        output_field=models.IntegerField(),
                    )
                )
                .first()
            )

            if content:
                # cache for 1 hour
                cache.set(cache_key, content, timeout=3600)

            return content
        else:
            raise ValueError("content_id or content_tag must be provided.")
