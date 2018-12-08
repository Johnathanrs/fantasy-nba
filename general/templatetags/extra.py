from django import template

from general.models import *

register = template.Library()

@register.filter
def percent(val):
    return val if val else '-';

@register.filter()
def liked(uid, session):
    fav = session.get('fav', [])
    return 'done' if str(uid) in fav else ''

@register.filter 
def hot_sfp(player):
    if player['sfp'] >= player['afp'] + 5:
        return 'text-danger font-weight-bold'  
    elif player['sfp'] <= player['afp'] - 5:
        return 'text-primary font-weight-bold'
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

@register.filter
def team(opponent):
    return opponent.strip('@')

@register.filter
def vs(opponent):
    return '@' if '@' in opponent else 'vs'
