from django import template

from pyaa.helpers.status import StatusHelper

register = template.Library()


@register.filter
def status_bg_color_hex(value):
    return StatusHelper.get_status_color(value, "hex")["bg"]


@register.filter
def status_text_color_hex(value):
    return StatusHelper.get_status_color(value, "hex")["text"]


@register.filter
def status_bg_color_bs(value):
    return StatusHelper.get_status_color(value, "bs")["bg"]


@register.filter
def status_text_color_bs(value):
    return StatusHelper.get_status_color(value, "bs")["text"]
