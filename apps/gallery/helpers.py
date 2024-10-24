from django.db import models
from django.utils.translation import get_language

from apps.gallery.models import Gallery


class GalleryHelper:
    @staticmethod
    def get_gallery(gallery_id=None, gallery_tag=None):
        filter_kwargs = {"active": True}

        # if gallery_id is provided, ignore language and return the gallery directly
        if gallery_id:
            filter_kwargs["id"] = gallery_id
            return (
                Gallery.objects.filter(**filter_kwargs)
                .prefetch_related("gallery_photos")
                .first()
            )

        # if gallery_tag is provided, apply language priority logic (check both code_iso_639_1 and code_iso_language)
        elif gallery_tag:
            user_language = get_language()

            if user_language:
                user_language = user_language.lower()

            filter_kwargs["tag"] = gallery_tag

            # filter gallery based on language priority (user's language, then en-us, then global galleries)
            return (
                Gallery.objects.filter(**filter_kwargs)
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
        else:
            raise ValueError("gallery_id or gallery_tag must be provided.")

    @staticmethod
    def get_gallery_list():
        user_language = get_language()

        if user_language:
            user_language = user_language.lower()

        # only include galleries in the user's language or global (language=None)
        return (
            Gallery.objects.filter(
                models.Q(language__code_iso_639_1=user_language)
                | models.Q(language__code_iso_language=user_language)
                | models.Q(language__isnull=True),
                active=True,
            )
            .prefetch_related("gallery_photos")
            .order_by("-id")
        )
