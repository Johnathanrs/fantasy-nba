import urllib2

from bs4 import BeautifulSoup

import os
from os import sys, path
import django

import datetime

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *


def sync(type_, val):
    # bball -> roto
    val = val.strip().strip('@')
    conv = {
        'team': {
            'GSW': 'GS',
            'CHO': 'CHA',
            'NOP': 'NO',
            'SAS': 'SA',
            'BRK': 'BKN',
            'NYK': 'NY'
        },
        'name': {
            'Juan Hernangomez': 'Juancho Hernangomez',
            'CJ McCollum': 'C.J. McCollum',
            'Taurean Waller-Prince': 'Taurean Prince',
            'Derrick Jones': 'Derrick Jones Jr.'
        }
    }

    return conv[type_][val] if val in conv[type_] else val


def clean_unicode(name):
    unicode_map = {
        u'\u0107': 'c',
        u'\u0160': 'S',
        u'\u010d': 'c',
        u'\u016b': 'u',
        u'\xe1':   'a',
        u'\u0161': 's',
        u'\xfd':   'y',
        u'\u0146': 'n',
        u'\u0123': 'g',
        u'\xf2':   'o'
    }

    for key, val in unicode_map.items():
        name = name.replace(key, val)

    return name


def scrape(param):
    dp = "https://www.basketball-reference.com/friv/dailyleaders.fcgi?" + param
    print (dp)
    response = urllib2.urlopen(dp)
    r = response.read()

    soup = BeautifulSoup(r, "html.parser")

    try:
        date = soup.find("span", {"class": "button2 current"}).text
        date = datetime.datetime.strptime(date, '%b %d, %Y')

        table = soup.find("table", {"id":"stats"})
        player_rows = table.find("tbody")
        players = player_rows.find_all("tr")
    except Exception as e:
        print (e)
        return  # no players

    for player in players:
        try:
            if player.get('class'): # ignore header
                continue

            mp = player.find("td", {"data-stat":"mp"}).text.split(':')
            name = player.find("td", {"data-stat":"player"}).text.strip()
            name = clean_unicode(name)
            name = sync('name', name)
            team = player.find("td", {"data-stat":"team_id"}).text.strip()
            team = sync('team', team)
            opp = player.find("td", {"data-stat":"opp_id"}).text
            opp = sync('team', opp)
            uid = player.find("td", {"data-stat":"player"}).get('data-append-csv')
            player_ = Player.objects.filter(first_name__iexact=name.split(' ')[0],
                                            last_name__iexact=name.split(' ')[1],
                                            team=team)
            # update avatar for possible new players
            avatar = 'https://d2cwpp38twqe55.cloudfront.net/req/201808311/images/players/{}.jpg'.format(uid)
            player_.update(avatar=avatar)

            trb = int(player.find("td", {"data-stat":"trb"}).text)
            ast = int(player.find("td", {"data-stat":"ast"}).text)
            blk = int(player.find("td", {"data-stat":"blk"}).text)
            stl = int(player.find("td", {"data-stat":"stl"}).text)
            tov = int(player.find("td", {"data-stat":"tov"}).text)
            pts = int(player.find("td", {"data-stat":"pts"}).text)
            fpts = pts + 1.2 * trb + 1.5 * ast + 3 * blk + 3 *stl - tov

            defaults = {
                'location': player.find("td", {"data-stat":"game_location"}).text,
                'opp': opp,
                'game_result': player.find("td", {"data-stat":"game_result"}).text,
                'mp': float(mp[0])+float(mp[1])/60,
                'fg': int(player.find("td", {"data-stat":"fg"}).text),
                'fga': player.find("td", {"data-stat":"fga"}).text,
                'fg_pct': player.find("td", {"data-stat":"fg_pct"}).text or None,
                'fg3': int(player.find("td", {"data-stat":"fg3"}).text),
                'fg3a': player.find("td", {"data-stat":"fg3a"}).text,
                'fg3_pct': player.find("td", {"data-stat":"fg3_pct"}).text or None,
                'ft': int(player.find("td", {"data-stat":"ft"}).text),
                'fta': player.find("td", {"data-stat":"fta"}).text,
                'ft_pct': player.find("td", {"data-stat":"ft_pct"}).text or None,
                'trb': trb,
                'ast': ast,
                'stl': stl,
                'blk': blk,
                'tov': tov,
                'pf': player.find("td", {"data-stat":"pf"}).text,
                'pts': pts,
                'fpts': fpts
            }

            PlayerGame.objects.update_or_create(name=name, team=team, date=date, defaults=defaults)
        except (Exception) as e:
            print (e)
    

if __name__ == "__main__":
    for delta in range(3):
        date = datetime.datetime.now() + datetime.timedelta(days=-delta)
        param = 'month={}&day={}&year={}&type=all'.format(date.month, date.day, date.year)
        scrape(param)
