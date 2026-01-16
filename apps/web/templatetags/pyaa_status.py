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
def status_bg_color_frontend(value):
    return StatusHelper.get_status_color(value, "frontend")["bg"]


@register.filter
def status_text_color_frontend(value):
    return StatusHelper.get_status_color(value, "frontend")["text"]
