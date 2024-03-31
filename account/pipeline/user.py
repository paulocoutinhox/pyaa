import uuid

from language.models import Language
from main import settings

from ..enums import CustomerStatus
from ..models import Customer


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}
    else:
        is_new = True
        email = details.get("email")

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            language = Language.objects.first()

            customer = Customer(
                name=details.get("fullname", ""),
                email=email,
                language=language,
                status=CustomerStatus.ACTIVE,
                timezone=settings.DEFAULT_TIME_ZONE,
            )

            customer.setup_password_data(password=str(uuid.uuid4()))
            customer.setup_initial_data()
            customer.save()

        return {"is_new": is_new, "user": customer, "social": customer}
