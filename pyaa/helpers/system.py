from django.conf import settings


class SystemHelper:
    LANGUAGE_CURRENCY_MAP = {
        "pt-br": "BRL",
        "en-us": "USD",
        "es-es": "EUR",
    }

    @staticmethod
    def get_currency():
        language_code = settings.LANGUAGE_CODE.lower()
        return SystemHelper.LANGUAGE_CURRENCY_MAP.get(language_code, None)
