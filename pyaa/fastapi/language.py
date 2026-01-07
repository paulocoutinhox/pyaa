from django.conf import settings
from django.utils import translation
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # get language from accept-language header
        accept_language = request.headers.get("Accept-Language", settings.LANGUAGE_CODE)

        # parse language code (e.g., "pt-br" -> "pt-br", "en-US" -> "en-us")
        language = accept_language.split(",")[0].strip().lower()

        # get list of supported languages
        supported_languages = [lang[0] for lang in settings.LANGUAGES]

        # try exact match first (e.g., "pt-br")
        if language in supported_languages:
            selected_language = language
        else:
            # try base language code (e.g., "pt-br" -> "pt")
            language_base = language.split("-")[0]

            # find first language that starts with base code
            selected_language = None
            for supported_lang in supported_languages:
                if supported_lang.startswith(language_base):
                    selected_language = supported_lang
                    break

            # fall back to default language if not found
            if not selected_language:
                selected_language = settings.LANGUAGE_CODE

        # activate translation for this request
        translation.activate(selected_language)

        try:
            response = await call_next(request)
        finally:
            # deactivate translation after request
            translation.deactivate()

        return response


def setup(app: FastAPI):
    app.add_middleware(LanguageMiddleware)
