import requests
import csv

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *

def main():
    try:
        url = 'https://www.rotowire.com/daily/tables/optimizer-nba.php?sport=NBA&site=FanDuel&projections=&type=main&slate=all'
        url = 'https://www.rotowire.com/daily/tables/optimizer-soc.php?league=EPL&site=FanDuel&projections=&type=main&slate=all'
        players = requests.get(url).json()

        with open('soc-players.csv', 'wb') as f:
            fields = players[0].keys()
            print fields
            w = csv.DictWriter(f, fields)
            w.writeheader()

            for ii in players:
                w.writerow(ii)
    except:
        pass

if __name__ == "__main__":
    main()
