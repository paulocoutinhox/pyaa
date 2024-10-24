from django.db import models
from django.utils.translation import get_language

from apps.content.models import Content


class ContentHelper:
    @staticmethod
    def get_content(content_id=None, content_tag=None):
        # define filter criteria based on passed parameters (id or tag)
        filter_kwargs = {"active": True}

        # if content_id is provided, ignore language and return the content directly
        if content_id:
            filter_kwargs["id"] = content_id
            return Content.objects.filter(**filter_kwargs).first()

        # if content_tag is provided, apply language priority logic
        elif content_tag:
            # get browser's language
            user_language = get_language()
            if user_language:
                user_language = user_language.lower()

            filter_kwargs["tag"] = content_tag

            # filter content based on language priority (user's language, then en-us, then any language)
            return (
                Content.objects.filter(**filter_kwargs)
                .order_by(
                    models.Case(
                        models.When(language__code_iso_language=user_language, then=0),
                        models.When(language__code_iso_language="en-us", then=1),
                        models.When(language__code_iso_language=None, then=2),
                        default=models.Value(3),
                        output_field=models.IntegerField(),
                    )
                )
                .first()
            )
        else:
            raise ValueError("content_id or content_tag must be provided.")
