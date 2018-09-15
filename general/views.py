# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import mimetypes
import datetime
from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg

from general.models import *
from general.lineup import *
from general import html2text


def players(request):
    return render(request, 'players.html', { 'data_sources': DATA_SOURCE })


@csrf_exempt
def get_players(request):
    ds = request.POST.get('ds')
    players = Player.objects.filter(data_source=ds).order_by('-proj_points')
    return HttpResponse(render_to_string('player-list_.html', locals()))


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


def current_season():
    today = datetime.date.today()
    return today.year if today > datetime.date(today.year, 10, 15) else today.year - 1


def player_detail(request, pid):
    player = Player.objects.get(id=pid)
    year = current_season()
    games = get_games_(pid, 'all', '', year)
    avg_min = games.aggregate(Avg('mp'))
    avg_fpts = games.aggregate(Avg('fpts'))

    return render(request, 'player_detail.html', locals())


def player_match_up_board(request):
    return render(request, 'player-match-up-board.html', locals())


def formated_diff(val):
    fm = '{:.1f}' if val > 0 else '({:.1f})'
    return fm.format(abs(val))


POSITION_ORDER = {
    "PG": 0,
    "SG": 1,
    "SF": 2,
    "PF": 3,
    "C": 4
}

# order = 1: ascending, -1: descending
def get_ranking(players, sattr, dattr, order=1):
    players = sorted(players, key=lambda k: k[sattr]*order)
    ranking = 0
    prev_val = None
    for ii in players:
        if ii[sattr] != prev_val:
            prev_val = ii[sattr]
            ranking += 1
        ii[dattr] = ranking
    return players

@csrf_exempt
def player_match_up(request):
    loc = request.POST.get('loc')
    pos = request.POST.get('pos')
    pos = '' if pos == 'All' else pos
    ds = request.POST.get('ds')

    last_game = PlayerGame.objects.all().order_by('-date').first()
    players = []
    games = PlayerGame.objects.filter(date=last_game.date)

    if loc != 'all':
        games = games.filter(location=loc)

    for ii in games:
        names = ii.name.split(' ')
        team = 'GS' if ii.team == 'GSW' else ii.team
        player = Player.objects.filter(first_name=names[0], last_name=names[1], 
                                       team=team, data_source=ds).first()
        if player and pos in player.position:
            games = get_games_(player.id, 'all', '', current_season())
            ampg = games.aggregate(Avg('mp'))['mp__avg']
            smpg = games.filter(location='@').aggregate(Avg('mp'))['mp__avg']
            afp = games.aggregate(Avg('fpts'))['fpts__avg']
            sfp = games.filter(location='@').aggregate(Avg('fpts'))['fpts__avg']

            fellows = Player.objects.filter(position=player.position, team=player.team)
            fellows = ['{} {}'.format(jj.first_name, jj.last_name) for jj in fellows]

            players.append({
                'id': player.id,
                'name': ii.name,
                'team': ii.team,
                'loc': ii.location,
                'vs': ii.opp,
                'pos': player.position,
                'inj': html2text.html2text(player.injury) if player.injury else '-',
                'salary': player.salary,
                'ampg': ampg,
                'smpg': smpg,
                'mdiff': formated_diff(smpg-ampg),
                'afp': afp,
                'sfp': sfp,
                'pdiff': formated_diff(sfp-afp),
                'val': player.salary / 250 + 10,
                'opp': PlayerGame.objects.filter(team__contains=player.team, 
                                                 date__gte=datetime.date.today()+datetime.timedelta(-145),
                                                 name__in=fellows) \
                                         .order_by('-fpts').first().fpts
            })

    players = get_ranking(players, 'opp', 'opr')

    groups = {ii: [] for ii in POSITION_ORDER.keys()}
    for ii in players:
        groups[ii['pos']].append(ii)

    for ii in POSITION_ORDER.keys():
        if groups[ii]:
            groups[ii] = get_ranking(groups[ii], 'sfp', 'ppr', -1)
            groups[ii] = sorted(groups[ii], key=lambda k: -k['opr'])

    players = []
    for ii in POSITION_ORDER.keys():
        if groups[ii]:
            players += groups[ii] + [{}]

    return HttpResponse(render_to_string('player-board_.html', locals()))


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
        'chart': [[ii.date.strftime('%Y/%m/%d'), ii.fpts] for ii in games],
        'opps': opps
    }

    return JsonResponse(result, safe=False)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def _get_lineups(request):
    ids = request.POST.getlist('ids')
    locked = request.POST.getlist('locked')
    num_lineups = int(request.POST.get('num-lineups'))

    ids = [int(ii) for ii in ids]
    locked = [int(ii) for ii in locked]

    players = Player.objects.filter(id__in=ids)
    lineups = calc_lineups(players, num_lineups, locked)
    return lineups, players


def get_num_lineups(player, lineups):
    num = 0
    for ii in lineups:
        if ii.is_member(player):
            num = num + 1
    return num


def gen_lineups(request):
    lineups, players = _get_lineups(request)
    avg_points = mean([ii.projected() for ii in lineups])

    players_ = [{ 'name': '{} {}'.format(ii.first_name, ii.last_name), 
                  'team': ii.team, 
                  'id': ii.id, 
                  'avatar': ii.avatar, 
                  'lineups': get_num_lineups(ii, lineups)} 
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
