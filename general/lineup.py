import operator as op
from ortools.linear_solver import pywraplp
from general.models import *


class Roster:
    POSITION_ORDER = {
        "PG": 0,
        "SG": 1,
        "SF": 2,
        "PF": 3,
        "C": 4
    }

    def __init__(self, ds='FanDuel'):
        self.players = []
        self.ds = ds
        self.drop = None

    def add_player(self, player):
        self.players.append(player)

    def is_member(self, player):
        return player in self.players

    def get_num_teams(self):
        teams = set([ii.team for ii in self.players])
        return len(teams)

    def spent(self):
        return sum(map(lambda x: x.salary, self.players))

    def projected(self, gross=True):        # False
        lst = map(lambda x: x.proj_points, self.players)
        res = sum(lst)
        if self.ds == 'FanDuel' and not gross:
            drop = min(lst)
            for ii in self.players:
                if ii.proj_points == drop:
                    self.drop = str(ii)
                    break
            res = res - drop
        return res

    def position_order(self, player):
        return self.POSITION_ORDER[player.position]

    def dict_position_order(self, player):
        if player['pos'] in self.POSITION_ORDER:
            return self.POSITION_ORDER[player['pos']] + 10.0 / player['salary']
        else:
            return 100

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def get_csv(self, ds):
        s = ''
        if ds == 'FanDuel': 
            s = ','.join(str(x) for x in self.sorted_players())+'\n'
        else:
            pos = {
                'DraftKings': ['PG', 'SG', 'SF', 'PF', 'C', 'PG,SG', 'SF,PF'],
                'Yahoo': ['PG', 'SG', 'PG,SG', 'SF', 'PF', 'SF,PF', 'C'],
                'Fanball': ['PG', 'SG', 'SF', 'PF', 'C', 'PG,SG', 'SF,PF,C']
            }
            pos = pos[ds]
            players = list(self.players)
            for ii in pos:
                for jj in players:
                    if jj.position in ii:
                        s += str(jj) + ','
                        players.remove(jj)
                        break
            s += str(players[0])+'\n'

        return s

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.projected()
        s += "\tCost: $%s" % self.spent()
        return s


POSITION_LIMITS = {
    'FanDuel': [
                   ["PG", 2, 2],
                   ["SG", 2, 2],
                   ["SF", 2, 2],
                   ["PF", 2, 2],
                   ["C", 1, 1]
               ],
    'DraftKings': [
                      ["PG", 1, 3],
                      ["SG", 1, 3],
                      ["SF", 1, 3],
                      ["PF", 1, 3],
                      ["C", 1, 2],
                      ["PG,SG", 3, 4],
                      ["SF,PF", 3, 4]
                  ],
    'Yahoo': [
                ["PG", 1, 3],
                ["SG", 1, 3],
                ["SF", 1, 3],
                ["PF", 1, 3],
                ["C", 1, 2],
                ["PG,SG", 3, 4],
                ["SF,PF", 3, 4]
            ],
    'Fanball': [
                ["PG", 1, 3],
                ["SG", 1, 3],
                ["SF", 1, 3],
                ["PF", 1, 3],
                ["C", 1, 3],
                ["PG,SG", 3, 4],
                ["SF,PF", 3, 4]
            ]
}

SALARY_CAP = {
    'FanDuel': 60000,
    'DraftKings': 50000,
    'Yahoo': 200,
    'Fanball': 55000
}

ROSTER_SIZE = {
    'FanDuel': 9,
    'DraftKings': 8,
    'Yahoo': 8,
    'Fanball': 8
}

TEAM_LIMIT = {
    'FanDuel': 3,
    'Yahoo': 3,
    'DraftKings': 2,
    'Fanball': 2
}

TEAM_MEMEBER_LIMIT = {
    'FanDuel': 4,
    'Yahoo': 6,
    'DraftKings': 8,
    'Fanball': 8
}

def get_lineup(ds, players, teams, locked, max_point, con_mul):
    solver = pywraplp.Solver('nba-lineup', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    variables = []

    for i, player in enumerate(players):
        if player.id in locked and ds != 'DraftKings':
            variables.append(solver.IntVar(1, 1, str(player)+str(i)))
        else:        
            variables.append(solver.IntVar(0, 1, str(player)+str(i)))

    objective = solver.Objective()
    objective.SetMaximization()

    for i, player in enumerate(players):
        objective.SetCoefficient(variables[i], player.proj_points)

    salary_cap = solver.Constraint(0, SALARY_CAP[ds])
    for i, player in enumerate(players):
        salary_cap.SetCoefficient(variables[i], player.salary)

    point_cap = solver.Constraint(0, max_point)
    for i, player in enumerate(players):
        point_cap.SetCoefficient(variables[i], player.proj_points)

    position_limits = POSITION_LIMITS[ds]
    for position, min_limit, max_limit in position_limits:
        position_cap = solver.Constraint(min_limit, max_limit)

        for i, player in enumerate(players):
            if player.position in position:
                position_cap.SetCoefficient(variables[i], 1)

    # no more than n players from one team (yahoo, fanduel)
    if TEAM_MEMEBER_LIMIT[ds] != ROSTER_SIZE[ds] and len(teams) > 2:
        for team in teams:
            team_cap = solver.Constraint(0, TEAM_MEMEBER_LIMIT[ds])
            for i, player in enumerate(players):
                if team == player.team:
                    team_cap.SetCoefficient(variables[i], 1)

    if ds == 'DraftKings':    # multi positional constraints
        for ii in con_mul:
            if players[ii[0]].id in locked:
                mul_pos_cap = solver.Constraint(1, 1)
            else:
                mul_pos_cap = solver.Constraint(0, 1)

            for jj in ii:
                mul_pos_cap.SetCoefficient(variables[jj], 1)

    size_cap = solver.Constraint(ROSTER_SIZE[ds], ROSTER_SIZE[ds])
    for variable in variables:
        size_cap.SetCoefficient(variable, 1)

    solution = solver.Solve()

    if solution == solver.OPTIMAL:
        roster = Roster(ds)

        for i, player in enumerate(players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        return roster

def calc_lineups(players, num_lineups, locked, ds, cus_proj={}):
    result = []

    max_point = 10000
    teams = set([ii.team for ii in players])

    con_mul = []
    players_ = []
    idx = 0
    for ii in players:
        p = vars(ii)
        p.pop('_state')
        p['proj_points'] = float(cus_proj.get(str(ii.id), ii.proj_points))

        ci_ = []
        for jj in ii.actual_position.split('/'):
            ci_.append(idx)
            p['position'] = jj
            players_.append(Player(**p))
            idx += 1
        con_mul.append(ci_)
    players = players_

    while True:
        roster = get_lineup(ds, players, teams, locked, max_point, con_mul)

        if not roster:
            break

        max_point = roster.projected(gross=True) - 0.001
        
        if roster.get_num_teams() >= TEAM_LIMIT[ds] or len(teams) == 2:
            result.append(roster)
            if len(result) == num_lineups:
                break

    if ds == 'FanDuel':
        _result = [{ "roster": ii, "proj": ii.projected() } for ii in result]
        _result = sorted(_result, key=lambda k: k["proj"], reverse=True)
        result = [ii["roster"] for ii in _result]
    return result
