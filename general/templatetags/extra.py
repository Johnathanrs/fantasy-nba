from django import template

from general.models import *

register = template.Library()

@register.filter
def percent(val):
    return val if val else '-';

@register.filter
def liked(uid):
    return 'done' if uid and FavPlayer.objects.filter(player__uid=uid).exists() else ''

@register.filter 
def hot_sfp(player):
	if player['sfp'] >= player['afp'] + 5:
    	return 'text-danger'  
    elif player['sfp'] <= player['afp'] - 5:
    	return 'text-primary'
	else:
		return '' 

@register.filter
def ou_ml(game, team):
    if not game.ml:
        return ''

    if team in game.ml:
        return '( {} )'.format(game.ml.split(' ')[-1])
    else:
        return '( {} )'.format(int(game.ou))
