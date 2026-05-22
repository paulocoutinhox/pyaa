from django.conf import settings
from django.contrib.sites.models import Site


def site_processor(request):
    try:
        return {"site": Site.objects.get_current()}
    except:
        return {"site": None}


def cookie_consent_processor(request):
    return {
        "google_analytics_id": settings.GOOGLE_ANALYTICS_ID,
        "cookie_consent_version": settings.COOKIE_CONSENT_VERSION,
    }
