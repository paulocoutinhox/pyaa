from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.customer.models import Customer


def customer_required(view_func):
    """
    Decorator for views that require a customer object.
    Ensures that the user is logged in and has a customer account.
    Adds the customer to the request object as request.customer.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            request.customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper
