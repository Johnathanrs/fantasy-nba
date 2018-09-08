from django import template

from general.models import *

register = template.Library()

@register.filter
def percent(val):
    return val if val else '-';
