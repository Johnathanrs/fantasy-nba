# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from general.models import *

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'team', 'position', 'opponent', 'salary', 
                    'proj_points', 'data_source', 'updated_at']
    search_fields = ['first_name', 'last_name', 'team']
    list_filter = ['data_source', 'position']


class PlayerGameAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'location', 'opp', 'game_result', 'mp', 'fg', 'fga', 'fg_pct',
                    'fg3', 'fg3a', 'fg3_pct', 'ft', 'fta', 'ft_pct', 'trb', 'ast', 'stl', 'blk',
                    'tov', 'pf', 'pts', 'fpts', 'date']
    search_fields = ['name', 'team']
    list_filter = ['team', 'location', 'game_result']


admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerGame, PlayerGameAdmin)
