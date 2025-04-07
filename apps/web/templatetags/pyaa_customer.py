from django import template

register = template.Library()


@register.simple_tag
def has_purchased_product(customer, product_id):
    """
    Check if a customer has purchased a specific product
    Usage: {% has_purchased_product user.customer product.id as has_purchased %}
    """
    if not customer:
        return False

    return customer.has_purchased_product(product_id)
