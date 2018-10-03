# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import mimetypes
import datetime
from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Q, Sum

from general.models import *
from general.lineup import *
from general import html2text
from general.color import *

POSITION = ['PG', 'SG', 'SF', 'PF', 'C']


def _get_game_today():
    return Game.objects.all()


def players(request):
    players = Player.objects.filter(data_source='FanDuel').order_by('first_name')
    return render(request, 'players.html', locals())


def lineup(request):
    data_sources = DATA_SOURCE
    games = _get_game_today()
    return render(request, 'lineup.html', locals())


@csrf_exempt
def fav_player(request):
    uid = request.POST.get('uid')
    player = Player.objects.filter(uid=uid).first()
    if FavPlayer.objects.filter(player=player).exists():
        FavPlayer.objects.filter(player=player).delete()
    else:
        FavPlayer.objects.create(player=player)

    return HttpResponse('ok')


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
    games = _get_game_today()
    return render(request, 'player-match-up-board.html', locals())


def team_match_up_board(request):
    games = _get_game_today()
    return render(request, 'team-match-up-board.html', locals())


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


def get_team_games(team):
    # get all games for the team last season
    season = current_season()
    q = Q(team__contains=team) & \
        Q(date__range=[datetime.date(season, 10, 1), datetime.date(season+1, 6, 30)])

    return PlayerGame.objects.filter(q)


def get_team_stat(team, loc='@'):
    loc_ = '@' if loc == '' else ''
    season = current_season()
    q = Q(opp__contains=team) & Q(location=loc) & \
        Q(date__range=[datetime.date(season, 10, 1), datetime.date(season+1, 6, 30)])
    a_teams = PlayerGame.objects.filter(q)
    a_teams_ = a_teams.values('date').annotate(trb=Sum('trb'), 
                                               ast=Sum('ast'),
                                               stl=Sum('stl'),
                                               blk=Sum('blk'),
                                               tov=Sum('tov'),
                                               pts=Sum('pts'))

    rpg = a_teams_.aggregate(Avg('trb'))['trb__avg']
    apg = a_teams_.aggregate(Avg('ast'))['ast__avg']
    spg = a_teams_.aggregate(Avg('stl'))['stl__avg']
    bpg = a_teams_.aggregate(Avg('blk'))['blk__avg']
    tpg = a_teams_.aggregate(Avg('tov'))['tov__avg']
    ppg = a_teams_.aggregate(Avg('pts'))['pts__avg']

    q = Q(team__contains=team) & Q(location=loc_) & \
        Q(date__range=[datetime.date(season, 10, 1), datetime.date(season+1, 6, 30)])
    s_teams = PlayerGame.objects.filter(q)
    s_teams_ = s_teams.values('date').annotate(trb=Sum('trb'), 
                                               ast=Sum('ast'),
                                               stl=Sum('stl'),
                                               blk=Sum('blk'),
                                               tov=Sum('tov'),
                                               pts=Sum('pts'))

    s_rpg = s_teams_.aggregate(Avg('trb'))['trb__avg']
    s_apg = s_teams_.aggregate(Avg('ast'))['ast__avg']
    s_spg = s_teams_.aggregate(Avg('stl'))['stl__avg']
    s_bpg = s_teams_.aggregate(Avg('blk'))['blk__avg']
    s_tpg = s_teams_.aggregate(Avg('tov'))['tov__avg']
    s_ppg = s_teams_.aggregate(Avg('pts'))['pts__avg']

    res = {
        'team': team,
        'rpg': rpg,
        'apg': apg,
        'spg': spg,
        'bpg': bpg,
        'tpg': tpg,
        'ppg': ppg,
        'total': rpg+apg+spg+bpg+tpg+ppg,
        's_rpg': s_rpg,
        's_apg': s_apg,
        's_spg': s_spg,
        's_bpg': s_bpg,
        's_tpg': s_tpg,
        's_ppg': s_ppg,
        's_total': s_rpg+s_apg+s_spg+s_bpg+s_tpg+s_ppg
    }

    # FPA TM POS
    tm_pos = []
    # for each distinct match
    for ii in a_teams_:
        # players (games) in a match
        players = a_teams.filter(date=ii['date'])

        tm_pos_ = {}
        # for each position
        for pos in POSITION:
            # players in the position of the team
            players_ = Player.objects.filter(team=teamSync(players[0].team), position=pos)
            players_ = ['{} {}'.format(ip.first_name, ip.last_name) for ip in players_]
            tm_pos_[pos] = players.filter(name__in=players_).aggregate(Sum('fpts'))['fpts__sum'] or 0
        tm_pos.append(tm_pos_)
        print ii['date'], players[0].team, players[0].opp, players[0].location, tm_pos_
        
    for pos in POSITION:
        res[pos] = sum(ii[pos] for ii in tm_pos) / len(tm_pos)

    print '----------------------------'
    # for FPS TM POS
    tm_pos = []
    # for each distinct match
    for ii in s_teams_:
        # players (games) in a match
        players = s_teams.filter(date=ii['date'])

        tm_pos_ = {}
        # for each position
        for pos in POSITION:
            # players in the position of the team
            players_ = Player.objects.filter(team=teamSync(players[0].team), position=pos)
            players_ = ['{} {}'.format(ip.first_name, ip.last_name) for ip in players_]
            tm_pos_[pos] = players.filter(name__in=players_).aggregate(Sum('fpts'))['fpts__sum'] or 0
        tm_pos.append(tm_pos_)
        print ii['date'], players[0].team, players[0].opp, players[0].location, tm_pos_
    print '----------------------------'
    for pos in POSITION:
        res['s_'+pos] = sum(ii[pos] for ii in tm_pos) / len(tm_pos)

    return res


def get_team_info(team):
    team_games = get_team_games(team)
    # at most one game a day
    game_results = team_games.values('date', 'game_result').distinct()
    wins = game_results.filter(game_result='W').count()
    losses = game_results.filter(game_result='L').count()

    # get distinct players
    players_ = team_games.order_by('name').values('name', 'team').distinct()

    players = []

    for ii in players_:
        names = ii['name'].split(' ')
        team = teamSync(ii['team'])
        # print (names[0], names[1], team, ds, vs)
        player = Player.objects.filter(first_name=names[0], last_name=names[1], 
                                       team=team).first()
        if player:
            games = team_games.filter(name=ii['name'])
            ampg = games.aggregate(Avg('mp'))['mp__avg']
            afp = games.aggregate(Avg('fpts'))['fpts__avg']

            sfp = [ig.fpts for ig in games.order_by('-date')[:3]]
            sfp = sum(sfp)

            players.append({
                'avatar': player.avatar,
                'id': player.id,
                'name': ii['name'],
                'pos': player.position,
                'inj': html2text.html2text(player.injury) if player.injury else '-',
                'salary': player.salary,
                'gp': games.count(),
                'rpg': games.aggregate(Avg('trb'))['trb__avg'],
                'apg': games.aggregate(Avg('ast'))['ast__avg'],
                'spg': games.aggregate(Avg('stl'))['stl__avg'],
                'bpg': games.aggregate(Avg('blk'))['blk__avg'],
                'ppg': games.aggregate(Avg('pts'))['pts__avg'],
                'tpg': games.aggregate(Avg('tov'))['tov__avg'],
                'ampg': ampg,
                'afp': afp,
                'sfp': sfp / 3,
                'val': player.salary / 250 + 10
            })

    return { 
        'players': players, 
        'wins': wins,
        'losses': losses,
        'win_percent': wins * 100.0 / (wins + losses)
    }


def filter_players_fpa(team, min_afp, max_afp):
    info = json.loads(TMSCache.objects.filter(team=team, type=1).first().body)
    players = []

    for ii in range(len(info['players'])):
        afp = info['players'][ii]['afp']
        if min_afp <= afp <= max_afp:
            players.append(info['players'][ii])
    info['players'] = players
    return info


@csrf_exempt
def team_match_up(request):
    min_afp = float(request.POST.get('min_afp'))
    max_afp = float(request.POST.get('max_afp'))

    game = request.POST.get('game')
    game = Game.objects.get(id=game)

    teams = {
        'home': filter_players_fpa(game.home_team, min_afp, max_afp),
        'home_stat': json.loads(TMSCache.objects.filter(team=game.home_team, type=2).first().body),
        'away': filter_players_fpa(game.visit_team, min_afp, max_afp),
        'away_stat': json.loads(TMSCache.objects.filter(team=game.visit_team, type=2).first().body)
    }

    return HttpResponse(render_to_string('team-board_.html', locals()))


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
    games = request.POST.get('games').split(';')

    if len(games) > 1:
        q = Q()
        for game in games:
            if game:
                teams = game.split('-')
                q |= (Q(team__contains=teams[0]) & Q(opp__contains=teams[1])) | \
                     (Q(team__contains=teams[1]) & Q(opp__contains=teams[0])) 
    else:
        q = Q(name=-1)   # no result

    last_game = PlayerGame.objects.all().order_by('-date').first()
    players = []
    games = PlayerGame.objects.filter(Q(date=last_game.date) & q)

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
                        'avatar': player.avatar,
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

    groups = {ii: [] for ii in POSITION}

    colors = linear_gradient('#90EE90', '#137B13', num_opr)['hex']

    for ii in players:
        ii['color'] = str(colors[ii['opr']-1])
        groups[ii['pos']].append(ii)


    for ii in POSITION:
        if groups[ii]:
            groups[ii], _ = get_ranking(groups[ii], 'sfp', 'ppr', -1)
            groups[ii] = sorted(groups[ii], key=lambda k: -k['opr'])

    players = []
    for ii in POSITION:
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


def build_TMS_cache(request):
    all_teams = [ii['team'] for ii in PlayerGame.objects.values('team').distinct()]
    stat_home = [get_team_stat(ii, '@') for ii in all_teams]
    stat_away = [get_team_stat(ii, '') for ii in all_teams]

    attrs = stat_home[0].keys()
    for attr in attrs:
        if attr != 'team':
            order = -1 if attr.startswith('s_') else 1
            stat_home, _ = get_ranking(stat_home, attr, attr+'_rank', order)
            stat_away, _ = get_ranking(stat_away, attr, attr+'_rank', order)

    stat_home = { ii['team']: ii for ii in stat_home }
    stat_away = { ii['team']: ii for ii in stat_away }

    team_1 = []
    team_2 = []

    TMSCache.objects.all().delete()
    for game in Game.objects.all():
        if not game.home_team in team_1:
            TMSCache.objects.create(team=game.home_team, type=1, body=json.dumps(get_team_info(game.home_team)))
            team_1.append(game.home_team)

        if not game.visit_team in team_1:
            TMSCache.objects.create(team=game.visit_team, type=1, body=json.dumps(get_team_info(game.visit_team)))
            team_1.append(game.visit_team)

        if not game.home_team in team_2:
            TMSCache.objects.create(team=game.home_team, type=2, body=json.dumps(stat_home[game.home_team]))
            team_2.append(game.home_team)

        if not game.visit_team in team_2:
            TMSCache.objects.create(team=game.visit_team, type=2, body=json.dumps(stat_away[game.visit_team]))
            team_2.append(game.visit_team)

    return HttpResponse('success')
