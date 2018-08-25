from django import template

from general.models import *

register = template.Library()

@register.filter
def num_lineups(player, lineups):
    num = 0
    for ii in lineups:
        if ii.is_member(player):
            num = num + 1
    return num

@register.filter
def num_players(title):
    return Player.objects.filter(game_category__contains=title).count()
