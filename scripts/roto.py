import requests
import csv

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *
from general import html2text
import pdb

def get_players(data_source):
    try:
        url = 'https://www.rotowire.com/daily/tables/optimizer-nba.php?sport=NBA&' + \
              'site={}&projections=&type=main&slate=all'.format(data_source)

        players = requests.get(url).json()

        fields = ['first_name', 'last_name', 'money_line', 
                  'point_spread', 'position', 'proj_ceiling', 'opponent',
                  'proj_custom', 'proj_floor', 'proj_original', 'proj_points', 'proj_rotowire', 
                  'proj_third_party_one', 'proj_third_party_two', 'actual_position', 
                  'salary', 'team', 'team_points']
        print data_source, len(players)
        for ii in players:
            try:
                defaults = { key: str(ii[key]).replace(',', '') for key in fields }
                defaults['play_today'] = True

                defaults['injury'] = html2text.html2text(ii['injury']).strip()
                if data_source == 'FantasyDraft':
                    defaults['position'] = defaults['actual_position']
                obj = Player.objects.update_or_create(uid=ii['id'], data_source=data_source,
                                                      defaults=defaults)
            except Exception as e:
                pass
    except:
        print('*** Something is wrong ***')


if __name__ == "__main__":
    Player.objects.all().update(play_today=False)
    for ds in DATA_SOURCE:
        get_players(ds[0])
