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

    def __init__(self):
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def is_member(self, player):
        return player in self.players

    def get_num_teams(self):
        teams = set([ii.team for ii in self.players])
        return len(teams)

    def spent(self):
        return sum(map(lambda x: x.salary, self.players))

    def projected(self):
        return sum(map(lambda x: x.proj_points, self.players))

    def position_order(self, player):
        return self.POSITION_ORDER[player.position]

    def fav_position_order(self, obj):
        if obj.player.position in self.POSITION_ORDER:
            return self.POSITION_ORDER[obj.player.position]
        else:
            return 100

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def get_csv(self):
        s = ','.join(str(x) for x in self.sorted_players())
        s += ",{},{}\n".format(self.projected(), self.spent())
        return s

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.projected()
        s += "\tCost: $%s" % self.spent()
        return s


POSITION_LIMITS = [
    ["PG", 1, 3],
    ["SG", 1, 3],
    ["SF", 1, 3],
    ["PF", 1, 3],
    ["C", 1, 2]
]

ROSTER_SIZE = 8


def get_lineup(players, teams, SALARY_CAP, MAX_POINT, locked):
    solver = pywraplp.Solver('nba-lineup', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    variables = []

    for player in players:
        if player.id in locked:
            variables.append(solver.IntVar(1, 1, str(player)))
        else:        
            variables.append(solver.IntVar(0, 1, str(player)))

    objective = solver.Objective()
    objective.SetMaximization()

    for i, player in enumerate(players):
        objective.SetCoefficient(variables[i], player.proj_points)

    salary_cap = solver.Constraint(0, SALARY_CAP)
    for i, player in enumerate(players):
        salary_cap.SetCoefficient(variables[i], player.salary)

    point_cap = solver.Constraint(0, MAX_POINT)
    for i, player in enumerate(players):
        point_cap.SetCoefficient(variables[i], player.proj_points)

    for position, min_limit, max_limit in POSITION_LIMITS:
        position_cap = solver.Constraint(min_limit, max_limit)

        for i, player in enumerate(players):
            if position == player.position:
                position_cap.SetCoefficient(variables[i], 1)

    for team in teams:
        team_cap = solver.Constraint(0, 4)
        for i, player in enumerate(players):
            if team == player.team:
                team_cap.SetCoefficient(variables[i], 1)

    size_cap = solver.Constraint(ROSTER_SIZE, ROSTER_SIZE)
    for variable in variables:
        size_cap.SetCoefficient(variable, 1)

    solution = solver.Solve()

    if solution == solver.OPTIMAL:
        roster = Roster()

        for i, player in enumerate(players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        return roster


def calc_lineups(players, num_lineups, locked=[]):
    result = []
    SALARY_CAP = 60000
    MAX_POINT = 10000
    teams = set([ii.team for ii in players])

    while True:
        roster = get_lineup(players, teams, SALARY_CAP, MAX_POINT, locked)
        if not roster:
            break
        MAX_POINT = roster.projected() - 0.001
        if roster.get_num_teams() > 2:
            result.append(roster)
            if len(result) == num_lineups:
                break

    return result
