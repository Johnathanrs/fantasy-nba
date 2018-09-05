import urllib2

from bs4 import BeautifulSoup
from operator import itemgetter

import os
from os import sys, path
import django
import pdb

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
        table = soup.find("table", {"id":"stats"})
        player_rows = table.find("tbody")
        players = player_rows.find_all("tr")
    except Exception as e:
        return  # no players

    for player in players:
        try:
            if not player.get('class'): # ignore header
                name = player.find("td", {"data-stat":"player"}).text
                team_id = player.find("td", {"data-stat":"team_id"}).text
                game_location = player.find("td", {"data-stat":"game_location"}).text
                opp_id = player.find("td", {"data-stat":"opp_id"}).text
                game_result = player.find("td", {"data-stat":"game_result"}).text
                mp = player.find("td", {"data-stat":"mp"}).text
                fg = player.find("td", {"data-stat":"fg"}).text
                fga = player.find("td", {"data-stat":"fga"}).text
                fg_pct = player.find("td", {"data-stat":"fg_pct"}).text
                fg3 = player.find("td", {"data-stat":"fg3"}).text
                fg3a = player.find("td", {"data-stat":"fg3a"}).text
                fg3_pct = player.find("td", {"data-stat":"fg3_pct"}).text
                ft = player.find("td", {"data-stat":"ft"}).text
                fta = player.find("td", {"data-stat":"fta"}).text
                ft_pct = player.find("td", {"data-stat":"ft_pct"}).text
                orb = player.find("td", {"data-stat":"orb"}).text
                drb = player.find("td", {"data-stat":"drb"}).text
                trb = player.find("td", {"data-stat":"trb"}).text
                ast = player.find("td", {"data-stat":"ast"}).text
                stl = player.find("td", {"data-stat":"stl"}).text
                blk = player.find("td", {"data-stat":"blk"}).text
                tov = player.find("td", {"data-stat":"tov"}).text
                pf = player.find("td", {"data-stat":"pf"}).text
                pts = player.find("td", {"data-stat":"pts"}).text
                print name, team_id, game_location, opp_id, game_result, mp, fg, fga, fg_pct, fg3, fg3a, fg3_pct, ft, fta, ft_pct, orb, drb, trb, ast, stl, blk, tov, pf, pts

            # obj = Player.objects.update_or_create(
            #     name = player.find("td", {"class":"rwo-name"}).text.strip().replace('\n',' '),
            #     team=player.find("td", {"class":"rwo-team"}).text,
            #     defaults=defaults
            # )
        except (Exception) as e:
            print (e)
    

if __name__ == "__main__":
    main()
