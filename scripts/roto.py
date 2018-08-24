import csv
import requests

from bs4 import BeautifulSoup
from operator import itemgetter

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_soccer.settings")
django.setup()

from general.models import *

def main():
    dp = "https://www.rotowire.com/daily/soccer/optimizer.php"

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.2228.0 Safari/537.36'})

    r = session.get(dp)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            table = soup.find("div", {"id":"rwo-poolbox"})
            player_rows = table.find("tbody", {"id":"players"})
            players = player_rows.find_all("tr")
        except Exception as e:
            return  # no players

        for player in players:
            try:
                defaults = {
                    'salary': int(player.find("td", {"class":"rwo-salary"}).get('data-salary').replace(",","")),
                    'position': player.find("td", {"class":"rwo-pos"}).get('data-li'),
                    'points': float(player.find("td", {"class":"rwo-points"}).get('data-points')),
                    'value': float(player.find("td", {"class":"rwo-value"}).text)
                }

                obj = Player.objects.update_or_create(
                    name = player.find("td", {"class":"rwo-name"}).text.strip().replace('\n',' '),
                    team=player.find("td", {"class":"rwo-team"}).text,
                    defaults=defaults
                )
            except (Exception) as e:
                print (e)
        

if __name__ == "__main__":
    main()
