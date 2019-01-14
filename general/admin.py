# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import csv
import datetime
import mimetypes

from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.http import HttpResponse
from django.forms.models import model_to_dict

from rangefilter.filter import DateRangeFilter

from general.models import *


def write_report(queryset, path, result_csv_fields):
    result = open(path, 'w')
    result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
    result_csv.writeheader()

    for game in queryset:
        game_ = model_to_dict(game, fields=result_csv_fields)

        try:
            result_csv.writerow(game_)
        except Exception, e:
            print game_

    result.close()


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position', 'team', 'opponent', 'salary', 'play_today', 
                    'proj_points', 'data_source', 'created_at', 'updated_at', 'avatar']
    search_fields = ['first_name', 'last_name', 'team']
    list_filter = ['team', 'data_source', 'position', 'play_today']
    actions = ['export_players']

    def export_players(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ids = ','.join([str(item.id) for item in queryset])
        fields = ['first_name', 'last_name', 'position', 'team', 'salary', 'proj_points', 'data_source', 'avatar']

        path = "/tmp/nba_players.csv"
        write_report(queryset, path, fields)
        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) 
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) 
        return response

    export_players.short_description = "Export CSV" 


class PlayerGameAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'location', 'opp', 'game_result', 'mp', 'fg', 'fga', 'fg_pct',
                    'fg3', 'fg3a', 'fg3_pct', 'ft', 'fta', 'ft_pct', 'trb', 'ast', 'stl', 'blk',
                    'tov', 'pf', 'pts', 'fpts', 'date']
    search_fields = ['name', 'team']
    list_filter = ['team', 'opp', 'location', 'game_result', ('date', DateRangeFilter)]
    actions = ['export_games']

    def export_games(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ids = ','.join([str(item.id) for item in queryset])
        fields = [f.name for f in PlayerGame._meta.get_fields() 
                  if f.name not in ['id', 'is_new']]

        path = "/tmp/nba_games.csv"
        write_report(queryset, path, fields)
        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) 
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) 
        return response

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
