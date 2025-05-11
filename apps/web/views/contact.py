from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.web.forms.contact import ContactForm


def contact_index_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES)

        if form.is_valid():
            form.send_email()
            messages.success(request, _("message.contact-message-sent"))
            return redirect("contact_index")
    else:
        form = ContactForm()

    return render(
        request,
        "pages/contact/index.html",
        {
            "form": form,
        },
    )


urlpatterns = [
    path(
        "contact/",
        contact_index_view,
        name="contact_index",
    ),
]
