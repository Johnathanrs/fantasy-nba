import requests
import csv

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_nba.settings")
django.setup()

from general.models import *
from general.views import *
from general import html2text
import pdb

def get_players(data_source):
    try:
        url = 'https://www.rotowire.com/daily/tables/optimizer-nba.php?sport=NBA&' + \
              'site={}&projections=&type=main&slate=all'.format(data_source)

        players = requests.get(url).json()

        fields = ['first_name', 'last_name', 'minutes', 'money_line', 
                  'over_under', 'point_spread', 'position', 'proj_ceiling', 'opponent',
                  'proj_custom', 'proj_floor', 'proj_original', 'proj_points', 'proj_rotowire', 
                  'proj_site', 'proj_third_party_one', 'proj_third_party_two', 'actual_position', 
                  'salary', 'salary_custom', 'salary_original', 'team', 'team_points', 'value']

        for ii in players:
            defaults = { key: str(ii[key]).replace(',', '') for key in fields }
            defaults['injury'] = html2text.html2text(ii['injury']).strip()
            if data_source == 'FantasyDraft':
                defaults['position'] = defaults['actual_position']
            obj = Player.objects.update_or_create(uid=ii['id'], data_source=data_source,
                                                  defaults=defaults)
    except:
        pass

if __name__ == "__main__":
    for ds in DATA_SOURCE:
        get_players(ds[0])

    # build_TMS_cache()
