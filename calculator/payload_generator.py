
from teams import get_all_last_matches_for_team
from calculator.both_teams_to_score import calculate_both_teams_to_score_score
from calculator.goals_over import calculate_over_x_goals_score
from calculator.match_result import calculate_match_result_score
import mongo as mg
import numpy as np
import pandas as pd


def match_score_payload(home_team, away_team, league_id):
    home_matches = get_all_last_matches_for_team(home_team, 20)
    away_matches = get_all_last_matches_for_team(away_team, 20)
    over_1_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 1)
    over_2_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 2)
    over_3_5_score = calculate_over_x_goals_score(home_matches, away_matches, home_team, away_team, league_id, 3)
    btts_score = calculate_both_teams_to_score_score(home_matches, away_matches, home_team, away_team, league_id)
    match_result_score = calculate_match_result_score(home_matches, away_matches, home_team, away_team, league_id)

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


def get_top_results(fixture_date):
    fix_date = fixture_date.strftime('%Y-%m-%d')
    matches = mg.get_single_info("upcoming_fixtures", {"date": fix_date})['fixtures']
    match_array = []

    for match in matches:
        if match['odds'] is not None:
            try:
                home_result_odds = [x for x in match['odds'] if x['id'] == 1][0]['values'][0]['odd']
            except IndexError:
                pass
            try:
                away_result_odds = [x for x in match['odds'] if x['id'] == 1][0]['values'][2]['odd']
            except IndexError:
                pass
            try:
                btts_odds = [x for x in match['odds'] if x['id'] == 8][0]['values'][0]['odd']
            except IndexError:
                pass
            over_under_odds = []
            try:
                over_under_odds = [x for x in match['odds'] if x['id'] == 5]
                over_1_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 1.5'][0]['odd']
            except IndexError:
                pass
            try:
                over_2_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 2.5'][0]['odd']
            except IndexError:
                pass
            try:
                over_3_5_odds = [x for x in over_under_odds[0]['values'] if x['value'] == 'Over 3.5'][0]['odd']
            except IndexError:
                pass
        else:
            home_result_odds = np.nan
            away_result_odds = np.nan
            btts_odds = np.nan
            over_1_5_odds = np.nan
            over_2_5_odds = np.nan
            over_3_5_odds = np.nan

        match_array.append({
            "date": fix_date,
            "league_id": match['league_id'],
            "league_name": match['league_name'],
            "home_name": match['home_name'],
            "away_name": match['away_name'],
            "home_result_score": match['scores']['home_team_result'],
            "home_result_odds": home_result_odds,
            "away_result_score": match['scores']['away_team_result'],
            "away_result_odds": away_result_odds,
            "btts_score": match['scores']['btts'],
            "btts_odds": btts_odds,
            "over_1_5_score": match['scores']['over_1_5_score'],
            "over_1_5_odds": over_1_5_odds,
            "over_2_5_score": match['scores']['over_2_5_score'],
            "over_2_5_odds": over_2_5_odds,
            "over_3_5_score": match['scores']['over_3_5_score'],
            "over_3_5_odds": over_3_5_odds

        })

    arr_json = pd.json_normalize(match_array)
    df = pd.DataFrame(data=arr_json)
    df2 = df.dropna()
    top_home_win = df2.nlargest(n=15, columns='home_result_score')
    top_away_win = df2.nlargest(n=15, columns='away_result_score')
    top_btts = df2.nlargest(n=15, columns='btts_score')
    top_over_1_5 = df2.nlargest(n=10, columns='over_1_5_score')
    top_over_2_5 = df2.nlargest(n=10, columns='over_2_5_score')
    top_over_3_5 = df2.nlargest(n=10, columns='over_3_5_score')
    print(top_home_win[['home_name', 'away_name', 'home_result_score']])
    print("\n###################\n")
    print(top_away_win[['home_name', 'away_name', 'away_result_score']])
    print("\n###################\n")
    print(top_btts[['home_name', 'away_name', 'btts_score']])
    print("\n###################\n")
    print(top_over_1_5[['home_name', 'away_name', 'over_1_5_score']])
    print("\n###################\n")
    print(top_over_2_5[['home_name', 'away_name', 'over_2_5_score']])
    print("\n###################\n")
    print(top_over_3_5[['home_name', 'away_name', 'over_3_5_score']])

    return top_away_win[['home_name', 'away_name', 'away_result_score']]