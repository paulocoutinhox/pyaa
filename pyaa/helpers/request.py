from django.utils.http import url_has_allowed_host_and_scheme


class RequestHelper:
    @staticmethod
    def get_next_url(request):
        next_url = request.GET.get("next") or request.POST.get("next")

        if not url_has_allowed_host_and_scheme(
            url=next_url, allowed_hosts={request.get_host()}
        ):
            next_url = None

        return next_url
