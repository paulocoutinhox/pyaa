from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class CustomerGender(TextChoices):
    MALE = "male", _("enum.customer-gender.male")
    FEMALE = "female", _("enum.customer-gender.female")
    NONE = "none", _("enum.customer-gender.none")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class CustomerAddressType(TextChoices):
    MAIN = "main", _("enum.customer-address-type.main")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)
