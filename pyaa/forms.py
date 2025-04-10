from django.contrib.admin.forms import AdminAuthenticationForm
from django_recaptcha.fields import ReCaptchaField, ReCaptchaV3


class AdminAuthenticationFormWithCaptcha(AdminAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AdminAuthenticationFormWithCaptcha, self).__init__(*args, **kwargs)

        self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)
