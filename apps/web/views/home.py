from django.shortcuts import render
from django.urls import path

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


urlpatterns = [
    path(
        "",
        home_index_view,
        name="home",
    ),
]
