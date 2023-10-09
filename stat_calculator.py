from datetime import datetime

import leagues
import teams
from leagues import all_teams_in_league
import numpy as np
import mongo as mg

from teams import get_all_last_matches_for_team
from leagues import check_if_league, get_league_standings_stats
import fixtures
import pandas as pd
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
    try:
        if goals_for > goals_against:
            return "W"
        elif goals_for < goals_against:
            return "L"
        else:
            return "D"
    except TypeError:
        return None


# def match_result_calculator(result, n_matches):
#     if result == 0:
#         return 0
#     elif 0 < result < 2:
#         return 1
#     elif 2 <= result < 4:
#         return 2
#     elif 4 <= result < 6:
#         return 3
#     elif 6 <= result < 8:
#         return 5
#     elif 8 <= result < 10:
#         return 8
#     else:
#         return 13


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


##Team goals##
def team_goals_over(team, matches, n_matches, n_goals, home_away_all):
    goals_array = []
    counter = 0
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
            for x in matches:
                if x['home_id'] == team:
                    counter += 1
                    if x['score']['fulltime']['home'] > n_goals:
                        goals_array.append(x)
                        if counter == n_matches:
                            break

        else:
            for x in matches:
                if x['away_id'] == team:
                    counter += 1
                    if x['score']['fulltime']['away'] > n_goals:
                        goals_array.append(x)
                        if counter == n_matches:
                            break

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


def calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, goals):
    total_score = 0
    max_total = 0
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    try:
        # Last 5 games over x goals (60)
        last_5_home_team = [x for x in home_matches[:5] if
                            x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += total_occurrence_score(len(last_5_home_team), 5)
        max_total += 13

        # last 10 games over x goals
        last_10_home_team = [x for x in home_matches[:10] if
                             x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += total_occurrence_score(len(last_10_home_team), 10)
        max_total += 13

        # Last 5 home games for home team over x goals
        last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] +
                                         x['score']['fulltime']['away'] > goals and x['home_id'] == home_team]
        total_score += total_occurrence_score(len(last_5_home_team_home_matches), 5)
        max_total += 13

        # Last 5 home team team goals
        last_5_home_team_team_goals = team_goals_over(home_team, home_matches, 5, goals, home_away_all='all')
        total_score += total_occurrence_score(last_5_home_team_team_goals, 5)
        max_total += 13

        # Last 5 home team goal at home
        last_5_home_team_goals_at_home = team_goals_over(home_team, home_matches, 5, goals, home_away_all='home')
        total_score += total_occurrence_score(last_5_home_team_goals_at_home, 5)
        max_total += 13

        # last 5 games 0 goals for home team
        last_5_home_team_no_goals = team_no_goals_for_against(home_team, home_matches, 5, True)
        total_score += -total_occurrence_score(last_5_home_team_no_goals, 5)

        # last 5 home team clean sheets
        # last_5_home_team_clean_sheets = team_no_goals_for_against(home_team, home_matches, 5, False)
        # total_score += -total_occurrence_score(last_5_home_team_clean_sheets, 5)

        # last 5 home team 0-0
        last_5_home_team_no_score_draw = team_no_score_draw(home_matches, 5)
        total_score += -total_occurrence_score(last_5_home_team_no_score_draw, 5)

    except TypeError:
        pass

    try:
        last_5_away_team = [x for x in away_matches[:5] if
                            x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += total_occurrence_score(len(last_5_away_team), 5)
        max_total += 13

        last_10_away_team = [x for x in away_matches[:10] if
                             x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += total_occurrence_score(len(last_10_away_team), 10)
        max_total += 75

        # Last 5 away games for away team over x goals
        last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] +
                                         x['score']['fulltime']['away'] > goals and x['away_id'] == away_team]
        total_score += total_occurrence_score(len(last_5_away_team_away_matches), 5)
        max_total += 30

        # Last 5 away team team goals
        last_5_away_team_team_goals = team_goals_over(away_team, away_matches, 5, goals, home_away_all='all')
        total_score += total_occurrence_score(last_5_away_team_team_goals, 5)
        max_total += 13

        # Last 5 away team goals away
        last_5_away_team_goals_away = team_goals_over(away_team, away_matches, 5, goals, home_away_all='away')
        total_score += total_occurrence_score(last_5_away_team_goals_away, 5)
        max_total += 13

        # last 5 games 0 goals for away team
        last_5_away_team_no_goals = team_no_goals_for_against(home_team, home_matches, 5, True)
        total_score += -total_occurrence_score(last_5_away_team_no_goals, 5)

        # last 5 away team clean sheets
        # last_5_away_team_clean_sheets = team_no_goals_for_against(home_team, home_matches, 5, False)
        # total_score += -total_occurrence_score(last_5_away_team_clean_sheets, 5)

        # last 5 home team 0-0
        last_5_away_team_no_score_draw = team_no_score_draw(home_matches, 5)
        total_score += -total_occurrence_score(last_5_away_team_no_score_draw, 5)
    except TypeError:
        pass
    # last 10 h2h
    all_h2h = fixtures.get_all_h2h_matches(home_team, away_team)
    if len(all_h2h) > 4:
        last_5_h2h = [x for x in all_h2h[:5] if
                      x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += goals_calculator(len(last_5_h2h), 5)
        max_total += 30
    elif 0 > len(all_h2h) < 5:
        last_h2h = [x for x in all_h2h if
                    x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
        total_score += goals_calculator(len(last_h2h), 5)
        max_total += 15
    else:
        pass

    if len(home_matches) > 1 and len(away_matches) > 1 and leagues.check_if_league(league_id):

        home_team_standings = get_league_standings_stats(home_team, home_league_id)
        away_team_standings = get_league_standings_stats(away_team, away_league_id)

        # difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        no_of_teams_in_league = home_team_standings[1]
        total_score += standings_calculator(home_team_standings[0]['rank'],
                                            away_team_standings[0]['rank'],
                                            no_of_teams_in_league)
        max_total += 5

        average_home_goals_scored = home_team_standings[0]['all']['goals']['for'] / home_team_standings[0]['all']['played']
        average_away_goals_scored = away_team_standings[0]['all']['goals']['for'] / away_team_standings[0]['all']['played']
        average_home_goals_conceded = home_team_standings[0]['all']['goals']['against'] / home_team_standings[0]['all'][
            'played']
        average_away_goals_conceded = away_team_standings[0]['all']['goals']['against'] / away_team_standings[0]['all'][
            'played']
        home_for = average_goal_score(average_home_goals_scored, goals)
        away_for = average_goal_score(average_away_goals_scored, goals)
        home_against = average_goal_score(average_home_goals_conceded, goals)
        away_against = average_goal_score(average_away_goals_conceded, goals)

        total_score += home_for
        total_score += away_for
        total_score += home_against
        total_score += away_against
        max_total += 52

    elif len(home_matches) > 1 and len(away_matches) > 1 and not leagues.check_if_league(league_id):
        try:
            home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
            average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all'][
                'played']
            average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all'][
                'played']
            home_for = average_goal_score(average_home_goals_scored, goals)
            home_against = average_goal_score(average_home_goals_conceded, goals)
            total_score += home_for
            total_score += home_against
            max_total += 26
        except IndexError:
            pass
        except TypeError:
            pass
        try:
            away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]
            average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all'][
                'played']
            average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all'][
                'played']
            away_for = average_goal_score(average_away_goals_scored, goals)
            away_against = average_goal_score(average_away_goals_conceded, goals)
            total_score += away_for
            total_score += away_against
            max_total += 26
        except IndexError:
            pass
        except TypeError:
            pass
    else:
        pass

    return round(total_score / max_total, 2)


def calculate_both_teams_to_score_score(home_matches, away_matches, home_team, away_team, league_id):
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0
    max_total = 0

    try:
        # Last 5 games btts
        last_5_home_team = [x for x in home_matches[:5] if
                            x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
        total_score += total_occurrence_score(len(last_5_home_team), 5)
        max_total += 13
        # last 10 games btts
        last_10_home_team = [x for x in home_matches[:10]
                             if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
        total_score += total_occurrence_score(len(last_10_home_team), 10)
        max_total += 13
        # Last 5 home games for home team btts
        last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                         x['score']['fulltime']['away'] > 0 and x['home_id'] == home_team]
        total_score += total_occurrence_score(len(last_5_home_team_home_matches), 5)
        max_total += 13

        # last 5 games 0 goals for home team
        last_5_home_team_no_goals = team_no_goals_for_against(home_team, home_matches, 5, True)
        total_score += -total_occurrence_score(last_5_home_team_no_goals, 5)

        # last 5 home team clean sheets
        last_5_home_team_clean_sheets = team_no_goals_for_against(home_team, home_matches, 5, False)
        total_score += -total_occurrence_score(last_5_home_team_clean_sheets, 5)

        # last 5 home team 0-0
        last_5_home_team_no_score_draw = team_no_score_draw(home_matches, 5)
        total_score += -total_occurrence_score(last_5_home_team_no_score_draw, 5)
    except TypeError:
        pass

    try:
        last_5_away_team = [x for x in away_matches[:5] if
                            x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
        total_score += total_occurrence_score(len(last_5_away_team), 5)
        max_total += 13
        last_10_away_team = [x for x in away_matches
                             if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
        total_score += total_occurrence_score(len(last_10_away_team), 10)
        max_total += 13

        # Last 5 away games for away team btts
        last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                         x['score']['fulltime']['away'] > 0 and x['away_id'] == away_team]
        total_score += total_occurrence_score(len(last_5_away_team_away_matches), 5)
        max_total += 13

        # last 5 games 0 goals for away team
        last_5_away_team_no_goals = team_no_goals_for_against(home_team, home_matches, 5, True)
        total_score += -total_occurrence_score(last_5_away_team_no_goals, 5)

        # last 5 away team clean sheets
        last_5_away_team_clean_sheets = team_no_goals_for_against(home_team, home_matches, 5, False)
        total_score += -total_occurrence_score(last_5_away_team_clean_sheets, 5)

        # last 5 home team 0-0
        last_5_away_team_no_score_draw = team_no_score_draw(home_matches, 5)
        total_score += -total_occurrence_score(last_5_away_team_no_score_draw, 5)
    except TypeError:
        pass

    # Last 10 Head 2 Head
    all_h2h = fixtures.get_all_h2h_matches(home_team, away_team)
    if len(all_h2h) > 4:
        last_5_h2h_btts = [x for x in all_h2h['fixtures'][:5] if x['score']['fulltime']['home'] > 0 and
                           x['score']['fulltime']['away'] > 0]
        total_score += goals_calculator(len(last_5_h2h_btts), 5)
        max_total += 30
    elif 0 > len(all_h2h) < 5:
        last_h2h_btts = [x for x in all_h2h['fixtures'][:5] if x['score']['fulltime']['home'] > 0 and
                         x['score']['fulltime']['away'] > 0]
        total_score += goals_calculator(len(last_h2h_btts), 5)
        max_total += 15
    else:
        pass

    if len(home_matches) > 1 and len(away_matches) > 1 and leagues.check_if_league(league_id):
        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

        no_of_teams_in_league = len(leagues.all_teams_in_league(league_id))
        total_score += standings_calculator(home_team_standings['rank'],
                                            away_team_standings['rank'],
                                            no_of_teams_in_league)
        max_total += 5

        average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all']['played']
        average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all']['played']
        average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all'][
            'played']
        average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all'][
            'played']
        home_for = average_goal_score(average_home_goals_scored, 1)
        away_for = average_goal_score(average_away_goals_scored, 1)
        home_against = average_goal_score(average_home_goals_conceded, 1)
        away_against = average_goal_score(average_away_goals_conceded, 1)

        total_score += home_for
        total_score += away_for
        total_score += home_against
        total_score += away_against
        max_total += 52

    elif len(home_matches) > 1 and len(away_matches) > 1 and not leagues.check_if_league(league_id):
        try:
            home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
            average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all'][
                'played']
            average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all'][
                'played']
            home_for = average_goal_score(average_home_goals_scored, 1)
            home_against = average_goal_score(average_home_goals_conceded, 1)
            total_score += home_for
            total_score += home_against
            max_total += 26
        except IndexError:
            pass
        except TypeError:
            pass
        try:
            away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]
            average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all'][
                'played']
            average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all'][
                'played']
            away_for = average_goal_score(average_away_goals_scored)
            away_against = average_goal_score(average_away_goals_conceded)
            total_score += away_for
            total_score += away_against
            max_total += 26
        except IndexError:
            pass
        except TypeError:
            pass
    else:
        pass
    return round(total_score / max_total, 2)


def calculate_match_result_score(home_matches, away_matches, home_team, away_team, league_id):
    total_score_home = 0
    total_score_away = 0

    max_total_home = 0
    max_total_away = 0
    home_result_array = []
    try:
        for home_team_match in home_matches[:10]:
            if home_team_match['home_id'] == home_team:
                home_result_array.append(match_result(home_team_match['score']['fulltime']['home'],
                                                      home_team_match['score']['fulltime']['away']))
            else:
                home_result_array.append(match_result(home_team_match['score']['fulltime']['away'],
                                                      home_team_match['score']['fulltime']['home']))
        total_score_home += total_occurrence_score(home_result_array.count('W'), 10)
        max_total_home += 13
        total_score_home += -total_occurrence_score(home_result_array.count('L'), 10)
        total_score_home += -total_occurrence_score(home_result_array.count('D'), 10)/4

    except TypeError:
        pass

    home_team_home_matches = fixtures.get_last_x_home_matches(home_team, 5)
    home_result_home_array = []

    try:
        for home_team_home_match in home_team_home_matches:
            if home_team_home_match['home_id'] == home_team:
                home_result_home_array.append(match_result(home_team_home_match['score']['fulltime']['home'],
                                                           home_team_home_match['score']['fulltime']['away']))
            else:
                home_result_home_array.append(match_result(home_team_home_match['score']['fulltime']['away'],
                                                           home_team_home_match['score']['fulltime']['home']))

        total_score_home += total_occurrence_score(home_result_home_array.count('W'), 5)
        max_total_home += 13
        total_score_home += -total_occurrence_score(home_result_array.count('L'), 5)
        total_score_home += -total_occurrence_score(home_result_array.count('D'), 5) / 4
    except TypeError:
        pass

    last_10_home_team_goals = []
    try:
        for x in home_matches[:10]:
            if x['home_id'] == home_team:
                last_10_home_team_goals.append(int(x['score']['fulltime']['home']))
            else:
                last_10_home_team_goals.append(int(x['score']['fulltime']['away']))
        avg_home_goals = np.average(last_10_home_team_goals)
        total_score_home += average_goal_score(avg_home_goals, 1)
        max_total_home += 13
    except TypeError:
        pass

    away_result_array = []
    try:
        for away_team_match in away_matches[:10]:
            if away_team_match['home_id'] == away_team:
                away_result_array.append(match_result(away_team_match['score']['fulltime']['home'],
                                                      away_team_match['score']['fulltime']['away']))
            else:
                away_result_array.append(match_result(away_team_match['score']['fulltime']['away'],
                                                      away_team_match['score']['fulltime']['home']))

        total_score_away += total_occurrence_score(away_result_array.count('W'), 10)
        max_total_away += 13
        total_score_away += -total_occurrence_score(away_result_array.count('L'), 10)
        total_score_away += -total_occurrence_score(away_result_array.count('D'), 10)/4

    except TypeError:
        pass

    away_team_away_matches = fixtures.get_last_x_away_matches(away_team, 5)
    away_result_away_array = []
    try:
        for away_team_away_match in away_team_away_matches:
            if away_team_away_match['home_id'] == home_team:
                away_result_away_array.append(match_result(away_team_away_match['score']['fulltime']['home'],
                                                           away_team_away_match['score']['fulltime']['away']))
            else:
                away_result_away_array.append(match_result(away_team_away_match['score']['fulltime']['away'],
                                                           away_team_away_match['score']['fulltime']['home']))

        total_score_away += total_occurrence_score(away_result_away_array.count('W'), 5)
        max_total_away += 13
        total_score_away += -total_occurrence_score(away_result_array.count('L'), 5)
        total_score_away += -total_occurrence_score(away_result_array.count('D'), 5) / 4
    except TypeError:
        pass

    last_10_away_team_goals = []
    try:
        for x in away_matches[:10]:
            if x['home_id'] == away_team:
                last_10_away_team_goals.append(int(x['score']['fulltime']['home']))
            else:
                last_10_away_team_goals.append(int(x['score']['fulltime']['away']))
        avg_away_goals = np.average(last_10_away_team_goals)
        total_score_away += average_goal_score(avg_away_goals, 1)
        max_total_away += 13
    except TypeError:
        pass

    # League #
    if leagues.check_if_league(league_id):
        home_team_standings = get_league_standings_stats(home_team, league_id)
        away_team_standings = get_league_standings_stats(away_team, league_id)
        no_of_teams_in_home_league = home_team_standings[1]
        no_of_teams_in_away_league = away_team_standings[1]
        difference_in_league_position = home_team_standings[0]['rank'] - away_team_standings[0]['rank']
        if difference_in_league_position > 0:
            total_score_home += -difference_in_league_position
            total_score_away += difference_in_league_position
        else:
            total_score_home += -difference_in_league_position * 1.5
            total_score_away += difference_in_league_position * 1.5
        max_total_home += (no_of_teams_in_home_league - 1) * 1.5
        max_total_away += no_of_teams_in_away_league - 1
    else:
        try:
            home_league = teams.get_team_league_from_id(home_team)
            away_league = teams.get_team_league_from_id(away_team)
            home_team_standings = get_league_standings_stats(home_team, home_league)
            away_team_standings = get_league_standings_stats(away_team, away_league)

            home_standings_score = 13 if home_team_standings[0]['rank'] < 4 else 5
            total_score_home += home_standings_score
            away_standings_score = 13 if away_team_standings[0]['rank'] < 4 else 5
            total_score_away += away_standings_score
            max_total_home += 13
            max_total_away += 13
        except TypeError:
            pass
        except IndexError:
            pass

    return round(total_score_home / max_total_home, 2), round(total_score_away / max_total_away, 2)


# def match_score_payload(home_team, away_team, league_id):
#     home_matches = get_all_last_matches_for_team(home_team, 20)
#     away_matches = get_all_last_matches_for_team(away_team, 20)
#     over_1_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 1)
#     over_2_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 2)
#     over_3_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 3)
#     btts_score = calculate_both_teams_to_score_score(home_matches, away_matches, home_team, away_team, league_id)
#     match_result_score = calculate_match_result_score(home_matches, away_matches, home_team, away_team, league_id)
#
#     return {
#         'home_team_result': match_result_score[0],
#         'away_team_result': match_result_score[1],
#         'btts': btts_score,
#         'over_1_5_score': over_1_5_score,
#         'over_2_5_score': over_2_5_score,
#         'over_3_5_score': over_3_5_score
#     }
#
#
# def analyse_fixture(fixture_id, league_id, fixture_date):
#     fix_date = fixture_date.strftime('%Y-%m-%d')
#     if mg.count_documents("upcoming_fixtures", {"date": fix_date}):
#         fix = mg.get_single_info("upcoming_fixtures", {"date": fix_date})
#         all_fixtures = fix['fixtures']
#         fixture = [x for x in all_fixtures if x['fixture_id'] == fixture_id]
#         payload = match_score_payload(fixture[0]['home_id'], fixture[0]['away_id'], league_id)
#         return payload
#
#
# def get_top_results(fixture_date):
#     fix_date = fixture_date.strftime('%Y-%m-%d')
#     matches = mg.get_single_info("upcoming_fixtures", {"date": fix_date})['fixtures']
#     match_array = []
#
#     for match in matches:
#         if match['odds'] is not None:
#             try:
#                 home_result_odds = [x for x in match['odds'] if x['id'] == 1][0]['values'][0]['odd']
#             except IndexError:
#                 pass
#             try:
#                 away_result_odds = [x for x in match['odds'] if x['id'] == 1][0]['values'][2]['odd']
#             except IndexError:
#                 pass
#             try:
#                 btts_odds = [x for x in match['odds'] if x['id'] == 8][0]['values'][0]['odd']
#             except IndexError:
#                 pass
#             over_under_odds = []
#             try:
#                 over_under_odds = [x for x in match['odds'] if x['id'] == 5]
#                 over_1_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 1.5'][0]['odd']
#             except IndexError:
#                 pass
#             try:
#                 over_2_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 2.5'][0]['odd']
#             except IndexError:
#                 pass
#             try:
#                 over_3_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 3.5'][0]['odd']
#             except IndexError:
#                 pass
#         else:
#             home_result_odds = np.nan
#             away_result_odds = np.nan
#             btts_odds = np.nan
#             over_1_5_odds = np.nan
#             over_2_5_odds = np.nan
#             over_3_5_odds = np.nan
#
#         match_array.append({
#             "date": fix_date,
#             "league_id": match['league_id'],
#             "league_name": match['league_name'],
#             "home_name": match['home_name'],
#             "away_name": match['away_name'],
#             "home_result_score": match['scores']['home_team_result'],
#             "home_result_odds": home_result_odds,
#             "away_result_score": match['scores']['away_team_result'],
#             "away_result_odds": away_result_odds,
#             "btts_score": match['scores']['btts'],
#             "btts_odds": btts_odds,
#             "over_1_5_score": match['scores']['over_1_5_score'],
#             "over_1_5_odds": over_1_5_odds,
#             "over_2_5_score": match['scores']['over_2_5_score'],
#             "over_2_5_odds": over_2_5_odds,
#             "over_3_5_score": match['scores']['over_3_5_score'],
#             "over_3_5_odds": over_3_5_odds
#
#         })
#
#     arr_json = pd.json_normalize(match_array)
#     df = pd.DataFrame(data=arr_json)
#     df2 = df.dropna()
#     top_home_win = df2.nlargest(n=15, columns='home_result_score')
#     top_away_win = df2.nlargest(n=15, columns='away_result_score')
#     top_btts = df2.nlargest(n=15, columns='btts_score')
#     top_over_1_5 = df2.nlargest(n=10, columns='over_1_5_score')
#     top_over_2_5 = df2.nlargest(n=10, columns='over_2_5_score')
#     top_over_3_5 = df2.nlargest(n=10, columns='over_3_5_score')
#     print(top_home_win[['home_name', 'away_name', 'home_result_score']])
#     print("\n###################\n")
#     print(top_away_win[['home_name', 'away_name', 'away_result_score']])
#     print("\n###################\n")
#     print(top_btts[['home_name', 'away_name', 'btts_score']])
#     print("\n###################\n")
#     print(top_over_1_5[['home_name', 'away_name', 'over_1_5_score']])
#     print("\n###################\n")
#     print(top_over_2_5[['home_name', 'away_name', 'over_2_5_score']])
#     print("\n###################\n")
#     print(top_over_3_5[['home_name', 'away_name', 'over_3_5_score']])
#
#     return top_away_win[['home_name', 'away_name', 'away_result_score']]
