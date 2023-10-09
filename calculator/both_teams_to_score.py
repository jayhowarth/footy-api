import leagues
import teams
from leagues import get_league_standings_stats
import fixtures
from calculator.scoring import total_occurrence_score, standings_calculator, average_goal_score, goals_calculator
from calculator.match_parser import team_no_goals_for_against, team_no_score_draw

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
