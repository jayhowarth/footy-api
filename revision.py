## Stat
import numpy as np


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
    if goals_for > goals_against:
        return "W"
    elif goals_for < goals_against:
        return "L"
    else:
        return "D"


def match_result_calculator(result):
    if result == 0:
        return 0
    elif 0 < result < 2:
        return 1
    elif 2 <= result < 4:
        return 2
    elif 4 <= result < 6:
        return 3
    elif 6 <= result < 8:
        return 5
    elif 8 <= result < 10:
        return 8
    else:
        return 13


def standings_calculator(home_team_standing, away_team_standing):
    diff = abs(home_team_standing - away_team_standing)
    if 1 <= diff < 4:
        return diff
    elif 4 <= diff < 8:
        return diff
    elif 8 <= diff < 14:
        return diff
    elif 14 <= diff < 16:
        return diff
    else:
        return diff * 2


def match_score_payload(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 20)
    away_matches = get_all_last_matches_for_team(away_team, 20)

    over_1_5_score = calculate_over_x_goals_score(home_matches,
                                                  away_matches,
                                                  home_team,
                                                  away_team,
                                                  league_id, 1)
    over_2_5_score = calculate_over_x_goals_score(home_matches,
                                                  away_matches,
                                                  home_team,
                                                  away_team,
                                                  league_id, 2)
    over_3_5_score = calculate_over_x_goals_score(home_matches,
                                                  away_matches,
                                                  home_team,
                                                  away_team,
                                                  league_id, 3)
    btts_score = calculate_both_teams_to_score_score(home_matches,
                                                     away_matches,
                                                     home_team,
                                                     away_team,
                                                     league_id)
    match_result_score = calculate_match_result_score(home_matches,
                                                      away_matches,
                                                      home_team,
                                                      away_team,
                                                      league_id)

    return {
        'home_team_result': match_result_score[0],
        'away_team_result': match_result_score[1],
        'btts': btts_score,
        'over_1_5_score': over_1_5_score,
        'over_2_5_score': over_2_5_score,
        'over_3_5_score': over_3_5_score
    }


##############################################

def calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, goals):
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0
    # Last 5 games over x goals
    last_5_home_team = [x for x in home_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += (len(last_5_home_team) * 2) if len(last_5_home_team) < 5 else 20
    last_5_away_team = [x for x in away_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += (len(last_5_away_team) * 2) if len(last_5_away_team) < 5 else 20

    # last 10 games over 1.5 goals
    last_10_home_team = [x for x in home_matches[:10] if
                         x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += len(last_10_home_team) if len(last_10_home_team) < 10 else 40
    last_10_away_team = [x for x in away_matches[:10] if
                         x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += len(last_10_away_team) if len(last_10_away_team) < 10 else 40

    # Last 5 home games for home team over 1.5 goals
    last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] +
                                     x['score']['fulltime']['away'] > goals and x['home_id'] == home_team]
    total_score += (len(last_5_home_team_home_matches) * 2) if len(last_5_home_team_home_matches) < 5 else 20

    # Last 5 away games for away team over 1.5 goals
    last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] +
                                     x['score']['fulltime']['away'] > goals and x['away_id'] == away_team]
    total_score += (len(last_5_away_team_away_matches) * 2) if len(last_5_away_team_away_matches) < 5 else 20

    # Last 5 home team team goals
    last_5_home_team_team_goals = []
    if len(home_matches) > 1:
        for x in home_matches[:5]:
            if x['home_id'] == home_team:
                if x['score']['fulltime']['home'] > goals:
                    last_5_home_team_team_goals.append(x)
            else:
                if x['score']['fulltime']['away'] > goals:
                    last_5_home_team_team_goals.append(x)
        total_score += (len(last_5_home_team_team_goals) * 3) if len(last_5_home_team_team_goals) < 5 else 20

    # Last 5 away team team goals
    last_5_away_team_team_goals = []
    if len(away_matches) > 1:
        for x in away_matches[:5]:
            if x['home_id'] == away_team:
                if x['score']['fulltime']['home'] > goals:
                    last_5_home_team_team_goals.append(x)
            else:
                if x['score']['fulltime']['away'] > goals:
                    last_5_home_team_team_goals.append(x)
        total_score += (len(last_5_away_team_team_goals) * 3) if len(last_5_away_team_team_goals) < 5 else 20

    ### Team No Goals scored/clean sheets
    last_10_home_team_no_goals = [x for x in home_matches[:10] if
                                  x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]

    ### H2H
    all_h2h = fixtures.get_all_h2h_matches(home_team, away_team)
    try:
        last_10_h2h = [x for x in all_h2h[:10] if
                       x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    except TypeError:
        last_10_h2h = []
    total_score += len(last_10_h2h) if len(last_10_h2h) < 8 else 25
    if len(home_matches) > 1 and len(away_matches) > 1 and leagues.check_if_league(league_id):
        # home_league_id = [x for x in home_matches[:10] if check_if_league(x['league_id'])][0]['league_id']

        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        # away_league_id = [x for x in away_matches[:10] if check_if_league(x['league_id'])][0]['league_id']
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

        difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        total_score += (difference_in_league_position * 2)

        average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all']['played']
        average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all']['played']
        average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all'][
            'played']
        average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all'][
            'played']
        multiplier_home_for = average_goal_score(average_home_goals_scored)
        multiplier_away_for = average_goal_score(average_away_goals_scored)
        multiplier_home_against = average_goal_score(average_home_goals_conceded)
        multiplier_away_against = average_goal_score(average_away_goals_conceded)

        total_score += round(average_home_goals_scored * multiplier_home_for)
        total_score += round(average_away_goals_scored * multiplier_away_for)
        total_score += round(average_home_goals_conceded * multiplier_home_against)
        total_score += round(average_away_goals_conceded * multiplier_away_against)

    return total_score


############## Functions


##Team goals##
def team_goals_over(team, matches, n_matches, n_goals, home_away_all):
    goals_array = []
    if len(matches) > 1:
        if home_away_all == 'all':
            for x in matches[:n_matches]:
                if x['home_id'] == team:
                    if x['score']['fulltime']['home'] > n_goals:
                        goals_array.append(x)
                else:
                    if x['score']['fulltime']['away'] > n_goals:
                        goals_array.append(x)
        elif home_away_all == 'home':
            for x in matches[:n_matches]:
                if x['home_id'] == team:
                    if x['score']['fulltime']['home'] > n_goals:
                        goals_array.append(x)
        else:
            for x in matches[:n_matches]:
                if x['away_id'] == team:
                    if x['score']['fulltime']['away'] > n_goals:
                        goals_array.append(x)

    return len(goals_array)


##No Goals##

def team_no_goals_for_against(team, matches, n_matches, no_goals_for):
    no_goals_array = []
    if len(matches) > 1 and no_goals_for:
        for x in matches[:n_matches]:
            if x['home_id'] == team:
                if x['score']['fulltime']['home'] == 0:
                    no_goals_array.append(x)
            else:
                if x['score']['fulltime']['away'] == 0:
                    no_goals_array.append(x)
    elif len(matches) > 1 and not no_goals_for:
        for x in matches[:n_matches]:
            if x['home_id'] == team:
                if x['score']['fulltime']['away'] == 0:
                    no_goals_array.append(x)
            else:
                if x['score']['fulltime']['home'] == 0:
                    no_goals_array.append(x)
    else:
        pass
    return len(no_goals_array)


def team_no_score_draw(matches, n_matches):
    no_score_array = []
    if len(matches) > 1:
        for x in matches[:n_matches]:
            if x['score']['fulltime']['home'] == 0 and x['score']['fulltime']['away'] == 0:
                no_score_array.append(x)
    return len(no_score_array)
