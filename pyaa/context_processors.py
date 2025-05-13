from django.contrib.sites.models import Site


def site_processor(request):
    try:
        return {"site": Site.objects.get_current()}
    except:
        return {"site": None}
