## Stat

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
