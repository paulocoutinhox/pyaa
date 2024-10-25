from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from pyaa.helpers.mail import MailHelper


class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("model.field.name"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": "required",
            }
        ),
    )

    email = forms.EmailField(
        label=_("model.field.email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "required": "required",
            }
        ),
    )

    message = forms.CharField(
        label=_("model.field.message"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "required": "required",
            }
        ),
    )

    captcha = CaptchaField(
        label=_("model.field.captcha"),
    )

    def send_email(self):
        subject = _("email.contact.subject")
        from_email = self.cleaned_data["email"]
        recipient_list = [settings.DEFAULT_TO_EMAIL]

        context = {
            "form": self,
        }

        MailHelper.send_mail(
            subject=subject,
            to=recipient_list,
            template="emails/site/contact.html",
            context=context,
            reply_to=[from_email],
        )
