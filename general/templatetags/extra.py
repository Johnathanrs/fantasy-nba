from django import template

from general.models import *

register = template.Library()

@register.filter
def percent(val):
    return int(val * 100) if val else '-';
