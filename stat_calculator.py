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
        return -25
    elif 0.2 < avg_goals < 0.6:
        return -10
    elif 0.6 < avg_goals < 1.0:
        return 0
    elif 1.0 < avg_goals < 1.5:
        return 5
    elif 1.5 < avg_goals < 2.0:
        return 10
    elif 2.0 < avg_goals < 3.0:
        return 20
    else:
        return 30


def match_result(goals_for, goals_against):
    if goals_for > goals_against:
        return "W"
    elif goals_for < goals_against:
        return "L"
    else:
        return "D"


def match_result_calculator(n):
    if n == 0:
        return -40
    elif 0 < n < 2:
        return -20
    elif 2 <= n < 4:
        return -5
    elif 4 <= n < 6:
        return 5
    elif 6 <= n < 8:
        return 15
    elif 8 <= n < 10:
        return 25
    else:
        return 40


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
            return -50
        elif 1 <= matches < 3:
            return -25
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
        return 25
    elif 1 > position < 3:
        return 15
    elif 3 > position < 7:
        return 5
    else:
        return 0


def calculate_over_x_goals_score(home_team, away_team, league_id, goals):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0
    max_total = 0
    # Last 5 games over x goals (60)
    last_5_home_team = [x for x in home_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += goals_calculator(len(last_5_home_team), 5)
    last_5_away_team = [x for x in away_matches[:5] if
                        x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += goals_calculator(len(last_5_away_team))

    # last 10 games over x goals (210)
    last_10_home_team = [x for x in home_matches if
                         x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += goals_calculator(len(last_10_home_team), 10)
    last_10_away_team = [x for x in away_matches if
                         x['score']['fulltime']['home'] + x['score']['fulltime']['away'] > goals]
    total_score += goals_calculator(len(last_10_away_team), 10)

    # Last 5 home games for home team over x goals (240)
    last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] +
                                     x['score']['fulltime']['away'] > goals and x['home_id'] == home_team]
    total_score += goals_calculator(len(last_5_home_team_home_matches), 5)

    # Last 5 away games for away team over x goals (270)
    last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] +
                                     x['score']['fulltime']['away'] > goals and x['away_id'] == away_team]
    total_score += goals_calculator(len(last_5_away_team_away_matches), 5)

    # Last 5 home team team goals (330)
    last_5_home_team_team_goals = []
    if len(home_matches) > 1:
        for x in home_matches[:5]:
            if x['home_id'] == home_team:
                if x['score']['fulltime']['home'] > goals:
                    last_5_home_team_team_goals.append(x)
            else:
                if x['score']['fulltime']['away'] > goals:
                    last_5_home_team_team_goals.append(x)
        # total_score += (len(last_5_home_team_team_goals) * 3) if len(last_5_home_team_team_goals) < 5 else 20
        total_score += (goals_calculator(len(last_5_home_team_team_goals), 5) * 2)

    # Last 5 away team team goals (390)
    last_5_away_team_team_goals = []
    if len(away_matches) > 1:
        for x in away_matches[:5]:
            if x['home_id'] == away_team:
                if x['score']['fulltime']['home'] > goals:
                    last_5_home_team_team_goals.append(x)
            else:
                if x['score']['fulltime']['away'] > goals:
                    last_5_home_team_team_goals.append(x)
        # total_score += (len(last_5_away_team_team_goals) * 3) if len(last_5_away_team_team_goals) < 5 else 20
        total_score += (goals_calculator(len(last_5_away_team_team_goals), 5) * 2)
    max_total = 390
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

        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

        difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        no_of_teams_in_league = len(leagues.all_teams_in_league(league_id))
        total_score += (difference_in_league_position * 2)
        max_total += (no_of_teams_in_league - 1) * 2

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

        max_total += 80

    elif len(home_matches) > 1 and len(away_matches) > 1 and not leagues.check_if_league(league_id):
        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

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

        max_total += 80
    else:
        pass

    return round(total_score / max_total)


def calculate_both_teams_to_score_score(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    home_league_id = teams.get_team_league_from_id(home_team)
    away_league_id = teams.get_team_league_from_id(away_team)
    total_score = 0
    max_total = 0

    # Last 5 games btts (60)
    last_5_home_team = [x for x in home_matches[:5] if
                        x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += goals_calculator(len(last_5_home_team), 5)
    last_5_away_team = [x for x in away_matches[:5] if
                        x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += goals_calculator(len(last_5_away_team), 5)

    # last 10 games btts (210)
    last_10_home_team = [x for x in home_matches
                         if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += goals_calculator(len(last_10_home_team), 10)
    last_10_away_team = [x for x in away_matches
                         if x['score']['fulltime']['home'] > 0 and x['score']['fulltime']['away'] > 0]
    total_score += goals_calculator(len(last_10_away_team), 10)

    # Last 5 home games for home team btts (240)
    last_5_home_team_home_matches = [x for x in home_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                     x['score']['fulltime']['away'] > 0 and x['home_id'] == home_team]
    total_score += goals_calculator(len(last_5_home_team_home_matches), 5)

    # Last 5 away games for away team btts (270)
    last_5_away_team_away_matches = [x for x in away_matches[:5] if x['score']['fulltime']['home'] > 0 and
                                     x['score']['fulltime']['away'] > 0 and x['away_id'] == away_team]
    total_score += goals_calculator(len(last_5_away_team_away_matches), 5)
    max_total = 270
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

        teams_in_league = len(all_teams_in_league(home_league_id)) - 2

        difference_in_league_position = abs(home_team_standings['rank'] - away_team_standings['rank'])
        position_bonus = -10 if difference_in_league_position - teams_in_league > 15 else 5
        max_total += 5
        total_score += position_bonus

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

        max_total += 80

    elif len(home_matches) > 1 and len(away_matches) > 1 and not leagues.check_if_league(league_id):
        home_team_standings = get_league_standings_stats(home_team, home_league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league_id)[0]

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

        max_total += 80
    else:
        pass
    return round(total_score / max_total)


def calculate_match_result_score(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 10)
    away_matches = get_all_last_matches_for_team(away_team, 10)
    total_score_home = 0
    total_score_away = 0

    max_total_home = 0
    max_total_away = 0
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

    max_total_home += 190
    max_total_away += 190

    if leagues.check_if_league(league_id):
        home_team_standings = get_league_standings_stats(home_team, league_id)[0]
        away_team_standings = get_league_standings_stats(away_team, league_id)[0]

        difference_in_league_position = home_team_standings['rank'] - away_team_standings['rank']
        if difference_in_league_position > 0:
            total_score_home += -difference_in_league_position
            total_score_away += difference_in_league_position
        else:
            total_score_home += -difference_in_league_position * 2
            total_score_away += difference_in_league_position * 2
        max_total_home += 35
        max_total_away += 20
    else:
        home_league = teams.get_team_league_from_id(home_team)
        away_league = teams.get_team_league_from_id(away_team)
        home_team_standings = get_league_standings_stats(home_team, home_league)[0]
        away_team_standings = get_league_standings_stats(away_team, away_league)[0]

        home_standings_score = 15 if home_team_standings < 4 else 5
        total_score_home += home_standings_score
        away_standings_score = 15 if away_team_standings < 4 else 5
        total_score_away += away_standings_score
        max_total_home += 15
        max_total_away += 15

    return round(total_score_home/max_total_home), round(total_score_away/max_total_away)


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
