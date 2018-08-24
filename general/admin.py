# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from general.models import *

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'team', 'salary', 'proj_points', 'data_source', 'created_at']
    search_fields = ['first_name', 'last_name']
    list_filter = ['data_source']

admin.site.register(Player, PlayerAdmin)
