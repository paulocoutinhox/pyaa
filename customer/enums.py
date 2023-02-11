from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class CustomerStatus(TextChoices):
    ACTIVE = "active", _("enum.customer-status.active")
    INACTIVE = "inactive", _("enum.customer-status.inactive")
    DELETED = "deleted", _("enum.customer-status.deleted")

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class CustomerGender(TextChoices):
    MALE = "male", _("enum.customer-gender.male")
    FEMALE = "female", _("enum.customer-gender.female")
    NONE = "none", _("enum.customer-gender.none")

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
