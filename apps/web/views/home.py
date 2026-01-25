from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.translation import check_for_language

from apps.banner.enums import BannerZone
from apps.banner.helpers import BannerHelper


def home_index_view(request):
    banners = BannerHelper.get_banners(BannerZone.HOME)

    return render(
        request,
        "pages/home/index.html",
        {
            "banners": banners,
        },
    )


def set_language_view(request, language_code):
    """
    Set language via GET request and redirect to home.
    This endpoint is SEO-friendly, allowing crawlers to index all language versions.
    """
    supported_languages = [lang[0] for lang in settings.LANGUAGES]

    if check_for_language(language_code) and language_code in supported_languages:
        lang_code = language_code
    else:
        lang_code = settings.LANGUAGE_CODE.split("-")[0]

    response = HttpResponseRedirect(reverse("home"))
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )

    return response


urlpatterns = [
    path(
        "",
        home_index_view,
        name="home",
    ),
    path(
        "lang/<str:language_code>/",
        set_language_view,
        name="set_language",
    ),
]
