from django import template

from pyaa.helpers.system import SystemHelper

register = template.Library()


@register.simple_tag
def get_currency():
    """
    Returns the system configured currency based on the current language.
    """
    return SystemHelper.get_currency()
