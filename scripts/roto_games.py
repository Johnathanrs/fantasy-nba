import requests
import datetime

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *
import pdb

def get_games():
    try:
        url = 'https://www.rotowire.com/daily/tables/schedule.php?sport=NBA&' + \
              'site=FanDuel&type=main&slate=all'

        games = requests.get(url).json()
        for ii in games:
          print (ii)
          ii.pop('exclude')
          ii.pop('home_score')
          ii.pop('visit_score')
          ii['date'] = datetime.datetime.strptime(ii['date'].split(' ')[1], '%I:%M%p')
          ii['date'] = datetime.datetime.combine(datetime.date.today(), ii['date'].time())
          ii['ou'] = float(ii['ou']) if ii['ou'] else 0
          Game.objects.create(**ii)
    except:
        pass

if __name__ == "__main__":
    get_games()
