from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class BannerZone(TextChoices):
    HOME = "home", _("enum.banner-zone.home")
    SIGNIN = "signin", _("enum.banner-zone.signin")
    SIGNUP = "signup", _("enum.banner-zone.signup")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class BannerAccessType(TextChoices):
    VIEW = "view", _("enum.banner-access-type.view")
    CLICK = "click", _("enum.banner-access-type.click")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)
