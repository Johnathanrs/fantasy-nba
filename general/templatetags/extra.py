from django import template

from general.models import *
from general import html2text

register = template.Library()

@register.filter
def percent(val):
    return val if val else '-';

@register.filter
def get_injury(player):
    return html2text.html2text(player.injury) if player.injury else '-'

@register.filter
def liked(uid):
    return 'done' if uid and FavPlayer.objects.filter(player__uid=uid).exists() else ''
