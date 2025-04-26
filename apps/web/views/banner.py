import json

from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.banner.enums import BannerAccessType
from apps.banner.helpers import BannerHelper


@csrf_exempt
@require_POST
def track_view_access(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        banner = BannerHelper.get_banner_by_token(token)
        if not banner:
            return JsonResponse({"error": "Banner not found"}, status=404)

        tracked = BannerHelper.track_banner_access(
            request, banner, BannerAccessType.VIEW
        )
        return JsonResponse({"success": tracked})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
@require_POST
def track_click_access(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        banner = BannerHelper.get_banner_by_token(token)
        if not banner:
            return JsonResponse({"error": "Banner not found"}, status=404)

        tracked = BannerHelper.track_banner_access(
            request, banner, BannerAccessType.CLICK
        )
        return JsonResponse({"success": tracked})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


urlpatterns = [
    path(
        "banner/track-view-access/",
        track_view_access,
        name="banner_track_view_access",
    ),
    path(
        "banner/track-click-access/",
        track_click_access,
        name="banner_track_click_access",
    ),
]
