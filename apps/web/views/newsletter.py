from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.newsletter.forms import NewsletterForm
from apps.newsletter.helpers import NewsletterHelper


def newsletter_subscribe_view(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            NewsletterHelper.subscribe(email)
            return redirect("newsletter_success")
    else:
        form = NewsletterForm()

    return render(
        request,
        "pages/newsletter/subscribe.html",
        {
            "form": form,
        },
    )


def newsletter_success_view(request):
    return render(
        request,
        "pages/newsletter/success.html",
    )


urlpatterns = [
    path(
        "newsletter/subscribe/",
        newsletter_subscribe_view,
        name="newsletter_subscribe",
    ),
    path(
        "newsletter/success/",
        newsletter_success_view,
        name="newsletter_success",
    ),
]
