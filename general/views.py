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
from django.db.models import Avg, Q

from general.models import *
from general.lineup import *
from general import html2text
from general.color import *

def players(request):
    data_sources = DATA_SOURCE
    games = {}
    for slate in SLATES:
        games[str(slate[0])] = Game.objects.filter(slate=slate[0])

    return render(request, 'players.html', locals())


@csrf_exempt
def get_players(request):
    ds = request.POST.get('ds')
    games = request.POST.get('games').split(';')

    if len(games) > 1:
        q = Q()
        for game in games:
            if game:
                teams = game.split('-')
                q |= (Q(team=teams[0]) & Q(opponent__contains=teams[1])) | \
                     (Q(team=teams[1]) & Q(opponent__contains=teams[0])) 
    else:
        q = Q(uid=-1)   # no result

    players = Player.objects.filter(Q(data_source=ds) & q).order_by('-proj_points')
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
    return players, ranking

def teamSync(team):
    team = team.strip().strip('@')
    conv = {
        'GSW': 'GS'
    }

    return conv[team] if team in conv else team

@csrf_exempt
def player_match_up(request):
    loc = request.POST.get('loc')
    pos = request.POST.get('pos')
    pos = '' if pos == 'All' else pos
    ds = request.POST.get('ds')
    min_afp = float(request.POST.get('min_afp'))
    min_sfp = float(request.POST.get('min_sfp'))
    max_afp = float(request.POST.get('max_afp'))
    max_sfp = float(request.POST.get('max_sfp'))

    last_game = PlayerGame.objects.all().order_by('-date').first()
    players = []
    games = PlayerGame.objects.filter(date=last_game.date)

    if loc != 'all':
        games = games.filter(location=loc)

    for ii in games:
        names = ii.name.split(' ')
        team = teamSync(ii.team)
        vs = teamSync(ii.opp)
        # print (names[0], names[1], team, ds, vs)
        player = Player.objects.filter(first_name=names[0], last_name=names[1], 
                                       team=team, data_source=ds, opponent__contains=vs).first()
        if player and pos in player.position:
            games = get_games_(player.id, 'all', '', current_season())
            ampg = games.aggregate(Avg('mp'))['mp__avg']
            smpg = games.filter(location='@').aggregate(Avg('mp'))['mp__avg']
            afp = games.aggregate(Avg('fpts'))['fpts__avg']
            sfp = games.filter(location='@').aggregate(Avg('fpts'))['fpts__avg']

            if min_afp <= afp <= max_afp:
                if min_sfp <= sfp <= max_sfp:
                    fellows = Player.objects.filter(position=player.position, team=player.team)
                    fellows = ['{} {}'.format(jj.first_name, jj.last_name) for jj in fellows]

                    players.append({
                        'id': player.id,
                        'name': ii.name,
                        'team': team,
                        'loc': ii.location,
                        'vs': vs,
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

    players, num_opr = get_ranking(players, 'opp', 'opr')

    POSITION_ORDER = ['PG', 'SG', 'SF', 'PF', 'C']
    groups = {ii: [] for ii in POSITION_ORDER}

    colors = linear_gradient('#90EE90', '#137B13', num_opr)['hex']

    for ii in players:
        ii['color'] = str(colors[ii['opr']-1])
        groups[ii['pos']].append(ii)


    for ii in POSITION_ORDER:
        if groups[ii]:
            groups[ii], _ = get_ranking(groups[ii], 'sfp', 'ppr', -1)
            groups[ii] = sorted(groups[ii], key=lambda k: -k['opr'])

    players = []
    for ii in POSITION_ORDER:
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
