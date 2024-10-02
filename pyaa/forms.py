from captcha.fields import CaptchaField
from django.contrib.admin.forms import AdminAuthenticationForm


class AdminAuthenticationFormWithCaptcha(AdminAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AdminAuthenticationFormWithCaptcha, self).__init__(*args, **kwargs)
        self.fields["captcha"] = CaptchaField()
