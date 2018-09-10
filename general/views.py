# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import mimetypes

import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.views.decorators.csrf import csrf_exempt

from general.models import *
from general.lineup import *

def players(request):
    return render(request, 'players.html', { 'data_sources': DATA_SOURCE })

@csrf_exempt
def get_players(request):
    ds = request.POST.get('ds')
    players = Player.objects.filter(data_source=ds).order_by('-proj_points')
    return HttpResponse(render_to_string('player-list_.html', locals()))

def get_num_lineups(player, lineups):
    num = 0
    for ii in lineups:
        if ii.is_member(player):
            num = num + 1
    return num

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def get_games_(pid, loc, opp, season):
    player = Player.objects.get(id=pid)
    games = PlayerGame.objects.filter(name='{} {}'.format(player.first_name, player.last_name),
                                      team=player.team,
                                      opp__contains=opp,
                                      date__range=[datetime.date(season, 10, 1), datetime.date(season+1, 6, 30)]) \
                              .order_by('-date')
    if loc != 'all':
        games = games.filter(location=loc).order_by('-date')
    return games

def player_detail(request, pid):
    player = Player.objects.get(id=pid)
    return render(request, 'player_detail.html', locals())

@csrf_exempt
def player_games(request):
    pid = request.POST.get('pid')
    loc = request.POST.get('loc')
    opp = request.POST.get('opp')
    season = int(request.POST.get('season'))

    games = get_games_(pid, loc, opp, season)

    opps = '<option value="">All</option>'
    for ii in sorted(set(games.values_list('opp', flat=True).distinct())):
        opps += '<option>{}</option>'.format(ii)

    result = {
        'game_table': render_to_string('game-list_.html', locals()),
        'chart': [[ii.date.strftime('%Y/%m/%d'), ii.pts] for ii in games],
        'opps': opps
    }

    return JsonResponse(result, safe=False)

def _get_lineups(request):
    ids = request.POST.getlist('ids')
    locked = request.POST.getlist('locked')
    num_lineups = int(request.POST.get('num-lineups'))

    ids = [int(ii) for ii in ids]
    locked = [int(ii) for ii in locked]

    players = Player.objects.filter(id__in=ids)
    lineups = calc_lineups(players, num_lineups, locked)
    return lineups, players

def gen_lineups(request):
    lineups, players = _get_lineups(request)
    avg_points = mean([ii.projected() for ii in lineups])

    players_ = [{ 'name': '{} {}'.format(ii.first_name, ii.last_name), 'team': ii.team, 'id': ii.id, 'lineups': get_num_lineups(ii, lineups)} 
                for ii in players if get_num_lineups(ii, lineups)]
    players_ = sorted(players_, key=lambda k: k['lineups'], reverse=True)
    return HttpResponse(render_to_string('player-lineup.html', locals()))

def export_lineups(request):
    lineups, _ = _get_lineups(request)
    # csv_fields = ['FWD', 'FWD', 'MID', 'MID', 'MID', 'DEF', 'DEF', 'GK', 'Projected', 'Salary']
    path = "/tmp/.fantasy_nba.csv"

    with open(path, 'w') as f:
        # f.write(','.join(csv_fields)+'\n')
        for ii in lineups:
            f.write(ii.get_csv())
    
    wrapper = FileWrapper( open( path, "r" ) )
    content_type = mimetypes.guess_type( path )[0]

    response = HttpResponse(wrapper, content_type = content_type)
    response['Content-Length'] = os.path.getsize( path ) # not FileField instance
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) # same here        
    return response

@csrf_exempt
def update_point(request):
    pid = int(request.POST.get('pid'))
    points = request.POST.get('val')
    Player.objects.filter(id=pid).update(proj_points=points)
    return HttpResponse('')
