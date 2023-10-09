def average_goal_score(avg_goals, n_goals):
    if avg_goals / n_goals < 0.2:
        return 0
    elif 0.2 <= avg_goals / n_goals < 0.6:
        return 1
    elif 0.6 <= avg_goals / n_goals < 0.8:
        return 2
    elif 0.8 <= avg_goals / n_goals < 1.0:
        return 3
    elif 1.0 <= avg_goals / n_goals < 1.5:
        return 5
    elif 1.5 <= avg_goals / n_goals < 2.5:
        return 8
    else:
        return 13


def total_occurrence_score(n_occ, n_matches):
    if n_occ == 0:
        return 0
    elif n_matches == 5:
        if n_occ == 1:
            return 1
        elif n_occ == 2:
            return 2
        elif n_occ == 3:
            return 5
        elif n_occ == 4:
            return 8
        else:
            return 13
    else:
        if 1 <= n_occ < 2:
            return 1
        elif 2 <= n_occ < 4:
            return 2
        elif 4 <= n_occ < 6:
            return 3
        elif 6 <= n_occ < 8:
            return 5
        elif 8 <= n_occ < 10:
            return 8
        else:
            return 13


def match_result(goals_for, goals_against):
    try:
        if goals_for > goals_against:
            return "W"
        elif goals_for < goals_against:
            return "L"
        else:
            return "D"
    except TypeError:
        return None


def goals_calculator(matches, n):
    if n == 5:
        if matches < 1:
            return -20
        elif matches == 1:
            return 0
        elif matches == 2:
            return 3
        elif matches == 3:
            return 5
        elif matches == 4:
            return 15
        else:
            return 30
    else:
        if matches < 1:
            return 0
        elif 1 <= matches < 3:
            return
        elif 3 <= matches < 5:
            return 0
        elif 5 <= matches < 7:
            return 10
        elif 7 <= matches < 9:
            return 20
        elif matches == 9:
            return 40
        else:
            return 75

def team_standings_calculator(position):
    if position == 1:
        return 13
    elif 1 > position < 3:
        return 8
    elif 3 > position < 7:
        return 5
    else:
        return 0

def standings_calculator(home_team_standing, away_team_standing, no_teams):
    diff = abs(home_team_standing - away_team_standing)
    if diff > no_teams - 4:
        return 5
    elif diff < 4:
        return 3
    else:
        return 1