import urllib2

from bs4 import BeautifulSoup

import os
from os import sys, path
import django
import pdb

from datetime import datetime

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *

def main():
    dp = "https://www.basketball-reference.com/friv/dailyleaders.fcgi"
    response = urllib2.urlopen(dp)
    r = response.read()

    soup = BeautifulSoup(r, "html.parser")
    # pdb.set_trace()

    try:
        date = soup.find("span", {"class": "button2 current"}).text
        date = datetime.strptime(date, '%b %d, %Y')
        last_game = PlayerGame.objects.all().order_by('-date').first()
        # if last_game and last_game.date == date.date():
        #     return

        table = soup.find("table", {"id":"stats"})
        player_rows = table.find("tbody")
        players = player_rows.find_all("tr")
    except Exception as e:
        return  # no players

    for player in players:
        try:
            if not player.get('class'): # ignore header
                mp = player.find("td", {"data-stat":"mp"}).text.split(':')
                name = player.find("td", {"data-stat":"player"}).text.strip()
                team = player.find("td", {"data-stat":"team_id"}).text.strip()
                team = 'GS' if team == 'GSW' else team
                uid = player.find("td", {"data-stat":"player"}).get('data-append-csv')
                player = Player.objects.filter(first_name__iexact=name.split(' ')[0],
                                               last_name__iexact=name.split(' ')[1],
                                               team=team)

                if player:# and not 'nba.ico' in player.first().avatar:
                    avatar = 'https://d2cwpp38twqe55.cloudfront.net/req/201808311/images/players/{}.jpg'.format(uid)
                    player.update(avatar=avatar)

                # obj = PlayerGame.objects.create(
                #     name = name,
                #     team = team,
                #     location = player.find("td", {"data-stat":"game_location"}).text,
                #     opp = player.find("td", {"data-stat":"opp_id"}).text,
                #     game_result = player.find("td", {"data-stat":"game_result"}).text,
                #     mp = float(mp[0])+float(mp[1])/60,
                #     fg = player.find("td", {"data-stat":"fg"}).text,
                #     fga = player.find("td", {"data-stat":"fga"}).text,
                #     fg_pct = player.find("td", {"data-stat":"fg_pct"}).text or None,
                #     fg3 = player.find("td", {"data-stat":"fg3"}).text,
                #     fg3a = player.find("td", {"data-stat":"fg3a"}).text,
                #     fg3_pct = player.find("td", {"data-stat":"fg3_pct"}).text or None,
                #     ft = player.find("td", {"data-stat":"ft"}).text,
                #     fta = player.find("td", {"data-stat":"fta"}).text,
                #     ft_pct = player.find("td", {"data-stat":"ft_pct"}).text or None,
                #     trb = player.find("td", {"data-stat":"trb"}).text,
                #     ast = player.find("td", {"data-stat":"ast"}).text,
                #     stl = player.find("td", {"data-stat":"stl"}).text,
                #     blk = player.find("td", {"data-stat":"blk"}).text,
                #     tov = player.find("td", {"data-stat":"tov"}).text,
                #     pf = player.find("td", {"data-stat":"pf"}).text,
                #     pts = player.find("td", {"data-stat":"pts"}).text,
                #     date = date
                # )
        except (Exception) as e:
            print (e)
    

if __name__ == "__main__":
    main()
