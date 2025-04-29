from django import forms
from django.utils.translation import gettext_lazy as _


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label=_("model.field.email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("form.placeholder.newsletter-email"),
            }
        ),
    )
