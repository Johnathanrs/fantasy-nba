# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

DATA_SOURCE = (
    ('FanDuel', 'FanDuel'),
    ('DraftKings', 'DraftKings'),
    ('Yahoo', 'Yahoo'),
    ('Head2Head', 'Head2Head'),
    ('Fanball', 'Fanball'),
    ('FantasyDraft', 'FantasyDraft')
)

class Player(models.Model):
    uid = models.IntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=250, default="/static/img/nba.ico")
    injury = models.TextField(blank=True, null=True)
    minutes = models.FloatField()
    money_line = models.IntegerField()
    opponent = models.CharField(max_length=50)
    over_under = models.FloatField()
    point_spread = models.FloatField()
    position = models.CharField(max_length=50)
    proj_ceiling = models.FloatField()
    proj_custom = models.FloatField()
    proj_floor = models.FloatField()
    proj_original = models.FloatField()
    proj_points = models.FloatField()
    proj_rotowire = models.FloatField()
    proj_site = models.FloatField()
    proj_third_party_one = models.FloatField()
    proj_third_party_two = models.FloatField()
    real_position = models.CharField(max_length=50, blank=True, null=True)
    salary = models.FloatField()
    salary_custom = models.FloatField()
    salary_original = models.FloatField()
    team = models.CharField(max_length=50)
    team_points = models.FloatField()
    value = models.FloatField()

    data_source = models.CharField(max_length=30, choices=DATA_SOURCE, default='FanDuel')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


GAME_RESULT = (
    ('W', 'Win'),
    ('L', 'Loss'),
)

class PlayerGame(models.Model):
    name = models.CharField("Player", max_length=50)
    team = models.CharField("Tm", max_length=50)
    location = models.CharField("H-A", max_length=50)
    opp = models.CharField("Vs", max_length=50)
    game_result = models.CharField("W-L", max_length=50, choices=GAME_RESULT)

    mp = models.FloatField("MP")
    fg = models.IntegerField("FG")
    fga = models.IntegerField("FGA")
    fg_pct = models.FloatField("FG%", null=True, blank=True)
    fg3 = models.IntegerField("3P")
    fg3a = models.IntegerField("3PA")
    fg3_pct = models.FloatField("3P%", null=True, blank=True)
    ft = models.IntegerField("FT")
    fta = models.IntegerField("FTA")
    ft_pct = models.FloatField("FT%", null=True, blank=True)
    trb = models.IntegerField("REB")
    ast = models.IntegerField("AST")
    stl = models.IntegerField("ST")
    blk = models.IntegerField("BLK")
    tov = models.IntegerField("TO")
    pf = models.IntegerField("PF")
    pts = models.IntegerField("PTS")
    fpts = models.FloatField("FPTS", default=-1)
    date = models.DateField()

    def __str__(self):
        return self.name


SLATES = (
    ('Thu-Mon', 'Thu-Mon'),
    ('Express', 'Express'),
    ('Main', 'Main'),
)

GAME_STATUS = (
    ('started', 'Started'),
    ('upcomming', 'Upcomming')
)

class Game(models.Model):
    home_team = models.CharField(max_length=20)
    visit_team = models.CharField(max_length=20)
    home_logo = models.CharField(max_length=120, null=True, blank=True)
    visit_logo = models.CharField(max_length=120, null=True, blank=True)
    ou = models.FloatField()
    ml = models.CharField(max_length=20)
    date = models.DateTimeField()
    game_status = models.CharField(max_length=50, choices=GAME_STATUS, default='started')
    slate = models.CharField(max_length=50, choices=SLATES)

    def __str__(self):
        return '{} - {}'.format(self.home_team, self.visit_team)
