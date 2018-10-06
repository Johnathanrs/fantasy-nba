from django import template

from general.models import *

register = template.Library()

@register.filter
def percent(val):
    return val if val else '-';

@register.filter
def liked(uid):
    return 'done' if uid and FavPlayer.objects.filter(player__uid=uid).exists() else ''
