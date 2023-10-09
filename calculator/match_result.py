import fixtures
import numpy as np
from calculator.scoring import match_result, total_occurrence_score, average_goal_score
from leagues import check_if_league, get_league_standings_stats
from teams import get_team_league_from_id


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
    if check_if_league(league_id):
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
            home_league = get_team_league_from_id(home_team)
            away_league = get_team_league_from_id(away_team)
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