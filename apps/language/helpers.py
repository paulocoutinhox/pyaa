from django.db.models import Q
from django.utils.translation import get_language

from apps.language.models import Language


class LanguageHelper:
    @staticmethod
    def get_current():
        # get the browser's language
        browser_language = get_language()

        # try to get the exact match for the language
        language = Language.objects.filter(
            Q(code_iso_language=browser_language) | Q(code_iso_639_1=browser_language)
        ).first()

        # if not found, try to get the language without the region code
        if not language and "-" in browser_language:
            language_code = browser_language.split("-")[0]
            language = Language.objects.filter(code_iso_639_1=language_code).first()

        # if still not found, use the first registered language
        if not language:
            language = Language.objects.first()

            if not language:
                raise Exception("No languages have been registered.")

        return language
