import leagues
from api_manager import APIManager as api
# from fixtures import get_fixture_statistics, get_fixture_events
import fixtures as fix
from datetime import datetime, timedelta
import mongo as mg
import json

teams_url = "https://api-football-v1.p.rapidapi.com/v3/teams"
leagues_url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
matches_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"


def get_team_name_from_id(team_id):
    querystring = {"id": team_id}
    record = mg.get_single_info("teams", querystring)
    return record['name']


def get_team_league_from_id(team_id):
    querystring = {"id": team_id}
    record = mg.get_single_info("teams", querystring)
    league_id = None
    try:
        league_id = record['current_league_id']
    except KeyError:
        update_teams_league(team_id)
        league_id = record['current_league_id']
    return league_id


def update_teams_previous_matches(team_id, num_matches):
    """
    updates x amount of previous matches for team id
    :param num_matches: number of matches to add
    :param team_id: int
    :return: number of matches added
    """
    querystring = {"team": team_id, "last": num_matches}
    fixture_response = api.get_request(matches_url, querystring)
    if fixture_response is not '':
        try:
            json_response = json.loads(fixture_response)
            total = json_response['results']
            fixtures = json_response['response']
        except TypeError:
            print('Error in fixture response')
            fixtures = None
            total = 0
    else:
        total = 0
        fixtures = []
    no_matches_added = 0
    if total > 0:
        for x in fixtures:
            if x['fixture']['status']['short'] == "FT":
                fixture_id = x['fixture']['id']
                league_id = x['league']['id']
                if not mg.document_exists("fixtures", {"id": fixture_id}):
                    home_stats, away_stats = fix.get_fixture_statistics(fixture_id, league_id)
                    fixture = {
                        "id": fixture_id,
                        "date": x['fixture']['date'],
                        "timestamp": x['fixture']['timestamp'],
                        "venue": x['fixture']['venue'],
                        "league_id": league_id,
                        "league_name": x['league']['name'],
                        "league_country": x['league']['country'],
                        "league_logo": x['league']['logo'],
                        "league_flag": x['league']['flag'],
                        "league_season": x['league']['season'],
                        "league_round": x['league']['round'],
                        "home_id": x['teams']['home']['id'],
                        "home_name": x['teams']['home']['name'],
                        "home_logo": x['teams']['home']['logo'],
                        "away_id": x['teams']['away']['id'],
                        "away_name": x['teams']['away']['name'],
                        "away_logo": x['teams']['away']['logo'],
                        "goals_home": x['goals']['home'],
                        "goals_away": x['goals']['away'],
                        "score": x['score'],
                        "events": fix.get_fixture_events(fixture_id, league_id),
                        "statistics_home": home_stats,
                        "statistics_away": away_stats,
                    }
                    mg.add_record("fixtures", fixture)
                    no_matches_added += 1
        mg.update_one_record("teams", {"id": team_id}, {"$set": {"last_match_update": datetime.utcnow()}})
        return no_matches_added
    else:
        return 0


def add_one_team(team_id):
    """
    Add a team to the database
    :param team_id: int
    :return: count if added
    """
    querystring = {"id": team_id}
    teams_response = api.get_request(teams_url, querystring)
    json_response = json.loads(teams_response)
    team_json = json_response['response'][0]
    team_id = team_json["team"]["id"]
    team = {
        "id": team_id,
        "name": team_json["team"]["name"],
        "code": team_json["team"]["code"],
        "country": team_json["team"]["country"],
        "founded": team_json["team"]["founded"],
        "national": team_json["team"]["national"],
        "logo": team_json["team"]["logo"],
        "venue": team_json["venue"]
    }

    count = mg.count_documents("teams", {"id": team_id})
    if count == 0 or count is None:
        mg.add_record("teams", team)
    else:
        mg.update_record("teams", {"id": team_id}, team)
    new_count = mg.count_documents("teams", {"id": team_id})
    return new_count


def check_when_last_team_fixtures_updated(team_id):
    team = mg.get_single_info("teams", {"id": team_id})
    try:
        last_updated = team['last_match_update']
        time_delta = datetime.utcnow() - last_updated
        if time_delta > timedelta(days=1):
            return True
        else:
            return False
    except KeyError:
        return True
    except TypeError:
        return True


def get_all_last_matches_for_team(team_id, num):
    query = [{"home_id": {"$eq": team_id}}, {"away_id": {"$eq": team_id}}]
    all_team_fixtures = mg.get_info_conditional_or("fixtures", query)
    sorted_fixtures = sorted(all_team_fixtures, key=lambda y: y['date'], reverse=True)
    team_fixtures = []
    for x in sorted_fixtures[:num]:
        team_fixtures.append(x)
    return sorted(team_fixtures, key=lambda y: y['date'], reverse=True)


def update_teams_league(team_id):
    status = ""
    query = {"id": team_id}
    if mg.check_team_last_updated("teams", query):
        querystring = {"team": str(team_id)}
        teams_response = api.get_request(leagues_url, querystring)
        json_response = json.loads(teams_response)
        league_list = json_response['response']
        for league in league_list:
            try:
                league_id = league['league']['id']
                is_league = leagues.check_if_league(league_id)
                if is_league:
                    mg.update_one_record("teams", {"id": team_id}, {"$set": {"current_league_id": league_id,
                                                                             "last_league_update": datetime.utcnow()}})
                    status = "Updated"
                    break
                else:
                    mg.update_one_record("teams", {"id": team_id}, {"$set": {"current_league_id": None,
                                                                             "last_league_update": datetime.utcnow()}})
                    status = "Not in league"
            except KeyError:
                mg.update_one_record("teams", {"id": team_id}, {"$set": {"current_league_id": None}})
                status = "Does Not Have League"
                return False
        return f"{status} {get_team_name_from_id(team_id)}"
    else:
        status = "up to date"
        return f"{get_team_name_from_id(team_id)} {status}"





