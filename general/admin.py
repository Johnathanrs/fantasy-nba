# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from rangefilter.filter import DateRangeFilter

from general.models import *
from general.utils import *


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position', 'team', 'opponent', 'salary', 'play_today', 
                    'proj_points', 'data_source', 'created_at', 'updated_at', 'avatar']
    search_fields = ['first_name', 'last_name', 'team']
    list_filter = ['team', 'data_source', 'position', 'play_today']
    actions = ['export_players']

    def export_players(self, request, queryset):
        fields = ['first_name', 'last_name', 'position', 'team', 'salary', 'proj_points', 'data_source', 'avatar']
        path = "/tmp/nba_players.csv"

        return download_response(queryset, path, fields)

    export_players.short_description = "Export CSV" 


class PlayerGameAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'location', 'opp', 'game_result', 'mp', 'fg', 'fga', 'fg_pct',
                    'fg3', 'fg3a', 'fg3_pct', 'ft', 'fta', 'ft_pct', 'trb', 'ast', 'stl', 'blk',
                    'tov', 'pf', 'pts', 'fpts', 'date']
    search_fields = ['name', 'team']
    list_filter = ['team', 'opp', 'location', 'game_result', ('date', DateRangeFilter)]
    actions = ['export_games']

    def export_games(self, request, queryset):
        fields = [f.name for f in PlayerGame._meta.get_fields() 
                  if f.name not in ['id', 'is_new']]
        path = "/tmp/nba_games.csv"

        return download_response(queryset, path, fields)

    export_games.short_description = "Export CSV" 


class GameAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'visit_team', 'ou', 'ml', 'game_status', 'date']
    search_fields = ['home_team', 'visit_team']
    list_filter = ['game_status']


class TMSCacheAdmin(admin.ModelAdmin):
    list_display = ['team', 'type', 'created_at']


admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerGame, PlayerGameAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(TMSCache, TMSCacheAdmin)
