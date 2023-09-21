from datetime import datetime

import leagues
import teams
from leagues import all_teams_in_league
import numpy as np
import mongo as mg

from teams import get_all_last_matches_for_team
from leagues import check_if_league, get_league_standings_stats
import fixtures

def average_goal_score(avg_goals):
    if avg_goals < 0.2:
        return -13
    elif 0.2 < avg_goals < 0.6:
        return -5
    elif 0.6 < avg_goals < 1.0:
        return 0
    elif 1.0 < avg_goals < 1.5:
        return 8
    elif 1.5 < avg_goals < 2.0:
        return 13
    elif 2.0 < avg_goals < 3.0:
        return 21
    else:
        return 34


def match_result(goals_for, goals_against):
    if goals_for > goals_against:
        return "W"
    elif goals_for < goals_against:
        return "L"
    else:
        return "D"


def match_result_calculator(result):
    if result == 0:
        return -21
    elif 0 < result < 2:
        return -13
    elif 2 <= result < 4:
        return -3
    elif 4 <= result < 6:
        return 5
    elif 6 <= result < 8:
        return 8
    elif 8 <= result < 10:
        return 13
    else:
        return 21


# def average_goal_calcuator(avg_goals):
#     if avg_goals < 0.5:
#         return 0
#     elif avg_goals >= 0.5 and avg_goals < 0.8:
#         return 3
#     elif avg_goals >= 0.8 and avg_goals < 1.0:
#         return 5
#     elif avg_goals >= 1.0 and avg_goals < 1.5:
#         return 8
#     elif avg_goals >= 1.5 and avg_goals < 2.0:
#         return 13
#     else:
#         return 21


def calculate_over_x_goals_score(home_team, away_team, league_id, goals):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0
    # Last 5 games over 1.5 goals
    last_5_home_team = [x for x in home_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += (len(last_5_home_team) * 2) if len(last_5_home_team) < 5 else 20
    last_5_away_team = [x for x in away_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += (len(last_5_away_team) * 2) if len(last_5_away_team) < 5 else 20

    # last 10 games over 1.5 goals
    last_10_home_team = [x for x in home_matches if
                         x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += len(last_10_home_team) if len(last_10_home_team) < 10 else 40
    last_10_away_team = [x for x in away_matches if
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

    all_h2h = fixtures.get_all_h2h_matches(home_team, away_team)
    try:
        last_10_h2h = [x for x in all_h2h[:10] if
                       x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    except TypeError:
        last_10_h2h = []
    total_score += len(last_10_h2h) if len(last_10_h2h) < 8 else 25
    if len(home_matches) > 1 and len(away_matches) > 1 and leagues.check_if_league(league_id):
        #home_league_id = [x for x in home_matches[:10] if check_if_league(x['league_id'])][0]['league_id']


        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        #away_league_id = [x for x in away_matches[:10] if check_if_league(x['league_id'])][0]['league_id']
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

        difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        total_score += (difference_in_league_position * 2)

        average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all']['played']
        average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all']['played']
        average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all']['played']
        average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all']['played']
        multiplier_home_for = average_goal_score(average_home_goals_scored)
        multiplier_away_for = average_goal_score(average_away_goals_scored)
        multiplier_home_against = average_goal_score(average_home_goals_conceded)
        multiplier_away_against = average_goal_score(average_away_goals_conceded)

        total_score += round(average_home_goals_scored * multiplier_home_for)
        total_score += round(average_away_goals_scored * multiplier_away_for)
        total_score += round(average_home_goals_conceded * multiplier_home_against)
        total_score += round(average_away_goals_conceded * multiplier_away_against)

    return total_score


def calculate_both_teams_to_score_score(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0

    # Last 5 games btts
    last_5_home_team = [x for x in home_matches[:5] if
                        x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += (len(last_5_home_team) * 2) if len(last_5_home_team) < 5 else 20
    last_5_away_team = [x for x in away_matches[:5] if
                        x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += (len(last_5_away_team) * 2) if len(last_5_away_team) < 5 else 20

    # last 10 games btts
    last_10_home_team = [x for x in home_matches
                         if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += len(last_10_home_team) if len(last_10_home_team) < 10 else 40
    last_10_away_team = [x for x in away_matches
                         if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += len(last_10_away_team) if len(last_10_away_team) < 10 else 40

    # Last 5 home games for home team btts
    last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                     x['score']['fulltime']['away'] > 0 and x['home_id'] == home_team]
    total_score += (len(last_5_home_team_home_matches) * 2) if len(last_5_home_team_home_matches) < 5 else 20

    # Last 5 away games for away team btts
    last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                     x['score']['fulltime']['away'] > 0 and x['away_id'] == away_team]
    total_score += (len(last_5_away_team_away_matches) * 2) if len(last_5_away_team_away_matches) < 5 else 20

    all_h2h = fixtures.get_all_h2h_matches(home_team, away_team)
    last_10_h2h_btts = [x for x in all_h2h['fixtures'][:10] if x['score']['fulltime']['home'] > 0 and
                        x['score']['fulltime']['away'] > 0 and x['away_id'] == away_team]
    total_score += (len(last_10_h2h_btts) * 2) if len(last_10_h2h_btts) < 7 else 25

    if len(home_matches) > 1 and len(away_matches) > 1 and leagues.check_if_league(league_id):
        # home_league_id = [x for x in home_matches[:10] if check_if_league(x['league_id'])][0]['league_id']
        # away_league_id = [x for x in away_matches[:10] if check_if_league(x['league_id'])][0]['league_id']

        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

        teams_in_league = len(all_teams_in_league(home_league_id)) - 2

        difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        position_bonus = -10 if difference_in_league_position - teams_in_league < 2 else 10

        total_score += position_bonus

        average_home_goals_scored = home_team_standings['all']['goals']['for'] / home_team_standings['all']['played']
        average_away_goals_scored = away_team_standings['all']['goals']['for'] / away_team_standings['all']['played']
        average_home_goals_conceded = home_team_standings['all']['goals']['against'] / home_team_standings['all']['played']
        average_away_goals_conceded = away_team_standings['all']['goals']['against'] / away_team_standings['all']['played']
        multiplier_home_for = average_goal_score(average_home_goals_scored)
        multiplier_away_for = average_goal_score(average_away_goals_scored)
        multiplier_home_against = average_goal_score(average_home_goals_conceded)
        multiplier_away_against = average_goal_score(average_away_goals_conceded)

        total_score += round(average_home_goals_scored * multiplier_home_for)
        total_score += round(average_away_goals_scored * multiplier_away_for)
        total_score += round(average_home_goals_conceded * multiplier_home_against)
        total_score += round(average_away_goals_conceded * multiplier_away_against)

    return total_score


def calculate_match_result_score(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    total_score_home = 0
    total_score_away = 0
    home_result_array = []
    for home_team_match in home_matches:
        if home_team_match['home_id'] == home_team:
            home_result_array.append(match_result(home_team_match['score']['fulltime']['home'],
                                                  home_team_match['score']['fulltime']['away']))
        else:
            home_result_array.append(match_result(home_team_match['score']['fulltime']['away'],
                                                  home_team_match['score']['fulltime']['home']))

    away_result_array = []
    for away_team_match in away_matches:
        if away_team_match['home_id'] == away_team:
            away_result_array.append(match_result(away_team_match['score']['fulltime']['home'],
                                                  away_team_match['score']['fulltime']['away']))
        else:
            away_result_array.append(match_result(away_team_match['score']['fulltime']['away'],
                                                  away_team_match['score']['fulltime']['home']))

    total_score_home += match_result_calculator(home_result_array.count('W'))
    total_score_away += match_result_calculator(away_result_array.count('W'))

    total_score_home += match_result_calculator(-home_result_array.count('L'))
    total_score_away += match_result_calculator(-away_result_array.count('L'))

    home_team_home_matches = fixtures.get_last_x_home_matches(home_team, 10)
    away_team_away_matches = fixtures.get_last_x_away_matches(away_team, 10)

    home_result_home_array = []
    for home_team_home_match in home_team_home_matches:
        if home_team_home_match['home_id'] == home_team:
            home_result_home_array.append(match_result(home_team_home_match['score']['fulltime']['home'],
                                                       home_team_home_match['score']['fulltime']['away']))
        else:
            home_result_home_array.append(match_result(home_team_home_match['score']['fulltime']['away'],
                                                       home_team_home_match['score']['fulltime']['home']))
    away_result_away_array = []
    for away_team_away_match in away_team_away_matches:
        if away_team_away_match['home_id'] == home_team:
            away_result_away_array.append(match_result(away_team_away_match['score']['fulltime']['home'],
                                                       away_team_away_match['score']['fulltime']['away']))
        else:
            away_result_away_array.append(match_result(away_team_away_match['score']['fulltime']['away'],
                                                       away_team_away_match['score']['fulltime']['home']))

    total_score_home += match_result_calculator(home_result_home_array.count('W'))
    total_score_away += match_result_calculator(away_result_away_array.count('W'))

    total_score_home += match_result_calculator(-home_result_home_array.count('L'))
    total_score_away += match_result_calculator(-away_result_away_array.count('L'))

    last_10_home_team_goals = []
    for x in home_matches[:10]:
        if x['home_id'] == home_team:
            last_10_home_team_goals.append(int(x['score']['fulltime']['home']))
        else:
            last_10_home_team_goals.append(int(x['score']['fulltime']['away']))

    last_10_away_team_goals = []
    for x in away_matches[:10]:
        if x['home_id'] == away_team:
            last_10_away_team_goals.append(int(x['score']['fulltime']['home']))
        else:
            last_10_away_team_goals.append(int(x['score']['fulltime']['away']))
    avg_home_goals = np.average(last_10_home_team_goals)
    avg_away_goals = np.average(last_10_away_team_goals)

    total_score_home += average_goal_score(avg_home_goals)
    total_score_away += average_goal_score(avg_away_goals)

    return total_score_home, total_score_away


def match_score_payload(home_team, away_team, league_id):
    over_1_5_score = calculate_over_x_goals_score(home_team, away_team, league_id, 1)
    over_2_5_score = calculate_over_x_goals_score(home_team, away_team, league_id, 2)
    over_3_5_score = calculate_over_x_goals_score(home_team, away_team, league_id, 3)
    btts_score = calculate_both_teams_to_score_score(home_team, away_team, league_id)
    match_result_score = calculate_match_result_score(home_team, away_team, league_id)

    return {
        'home_team_result': match_result_score[0],
        'away_team_result': match_result_score[1],
        'btts': btts_score,
        'over_1_5_score': over_1_5_score,
        'over_2_5_score': over_2_5_score,
        'over_3_5_score': over_3_5_score
    }


def analyse_fixture(fixture_id, league_id, fixture_date):
    fix_date = fixture_date.strftime('%Y-%m-%d')
    if mg.count_documents("upcoming_fixtures", {"date": fix_date}):
        fix = mg.get_single_info("upcoming_fixtures", {"date": fix_date})
        all_fixtures = fix['fixtures']
        fixture = [x for x in all_fixtures if x['fixture_id'] == fixture_id]
        payload = match_score_payload(fixture[0]['home_id'], fixture[0]['away_id'], league_id)
        return payload
