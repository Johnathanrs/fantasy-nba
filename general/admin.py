# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from general.models import *

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'team', 'position', 'opponent', 'salary', 
                    'proj_points', 'data_source', 'updated_at']
    search_fields = ['first_name', 'last_name', 'team']
    list_filter = ['data_source', 'position']

admin.site.register(Player, PlayerAdmin)
