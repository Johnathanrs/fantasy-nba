import requests
import datetime

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *
from general.views import *

def get_games():
    # try:
        for slate in ['all', 'Main']:
            url = 'https://www.rotowire.com/daily/tables/schedule.php?sport=NBA&' + \
                  'site=FanDuel&type=main&slate={}'.format(slate)

            games = requests.get(url).json()
            if games:
                Game.objects.all().delete()
                fields = ['game_status', 'ml', 'home_team', 'visit_team']
                for ii in games:
                    defaults = { key: str(ii[key]).replace(',', '') for key in fields }
                    defaults['date'] = datetime.datetime.strptime(ii['date'].split(' ')[1], '%I:%M%p')
                    # date is not used
                    defaults['date'] = datetime.datetime.combine(datetime.date.today(), defaults['date'].time())
                    defaults['ou'] = float(ii['ou']) if ii['ou'] else 0
                    Game.objects.create(**defaults)
                build_TMS_cache()
                build_player_cache()
                break
    # except:
    #     pass

if __name__ == "__main__":
    get_games()
