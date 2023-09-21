import betting_odds
import leagues
import main
import mongo as mg
import pytz
from dateutil import parser
from datetime import datetime, date, timedelta
import json
from api_manager import APIManager as api
from leagues import check_league_attributes, \
    check_if_league_has_events, \
    check_if_league_has_statistics, \
    get_all_main_leagues
# from teams import add_one_team, update_teams_previous_matches
import teams

matches_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"


def get_fixtures_by_date(fixture_date, filter_league):
    #converted_date = parser.parse(fixture_date)
    ppf = past_present_future(fixture_date)
    filtered_date = fixture_date.strftime('%Y-%m-%d')
    main_league_list = []
    if filter_league:
        main_league_list = get_all_main_leagues()
    else:
        pass
    querystring = {"date": filtered_date}
    has_odds = betting_odds.upcoming_fixtures_has_odds(fixture_date)
    exists = mg.document_exists("upcoming_fixtures", querystring)
    if exists and has_odds:
        fixture_document = mg.get_single_info("upcoming_fixtures", querystring)
        if filter_league:
            fixture_list = []
            for fixture in fixture_document['fixtures']:
                if fixture['league_id'] in main_league_list[1]:
                    fixture_list.append(fixture)
            return fixture_list
        else:
            return fixture_document['fixtures']
    else:
        # if not in database
        response = json.loads(api.get_request(main.fixtures_url, querystring))
        if ppf == 'past':
            status_array = ['FT']
        elif ppf == 'present':
            status_array = ['FT', 'HT', 'NS', '1H', '2H', 'ET']
        else:
            status_array = ['NS']
        x_status_array = ['FT', 'CANC', 'ABD', 'TBD']
        fixtures_list = []
        fixture_array = response['response']
        fixture_id_list = get_list_of_main_fixture_ids(fixture_array)
        betting_odds_list = betting_odds.get_betting_odds_for_date(filtered_date, fixture_id_list)

        for idx, x in enumerate(fixture_array):
            if filter_league:
                if x['league']['id'] not in main_league_list[1]:
                    pass  # del fixture_array[idx]
                else:
                    fixture_status = x['fixture']['status']['short']
                    date = x['fixture']['date']
                    league_attr = check_league_attributes(x['league']['id'])
                    fixture_date = datetime.fromisoformat(date)
                    now = datetime.utcnow().replace(tzinfo=pytz.utc)
                    fixture_in_future = now < fixture_date
                    if fixture_status in status_array:
                        fixtures_list.append(build_fixture_list(league_attr,
                                                                fixture_status,
                                                                date,
                                                                x,
                                                                betting_odds_list))
            else:
                fixture_status = x['fixture']['status']['short']
                date = x['fixture']['date']
                league_attr = check_league_attributes(x['league']['id'])
                fixture_date = datetime.fromisoformat(date)
                now = datetime.utcnow().replace(tzinfo=pytz.utc)
                if fixture_status in status_array:
                    fixtures_list.append(build_fixture_list(league_attr,
                                                            fixture_status,
                                                            date,
                                                            x,
                                                            betting_odds_list))
        if filter_league:
            save_upcoming_fixtures(filtered_date, fixtures_list)
        return fixtures_list


def past_present_future(fixture_date):
    today = datetime.now().date()
    # fix_date = fixture_date.strptime(fixture_date, '%Y-%m-%d')
    # fixture_date = fix_date.date()
    if fixture_date == today:
        return "current"
    elif fixture_date < today:
        return "past"
    else:
        return "future"


def build_fixture_list(league_attr, fixture_status, fixture_date, fixture, odds):
    fixture_id = fixture['fixture']['id']
    # timestamp = x['fixture']['timestamp']
    venue_name = fixture['fixture']['venue']['name']
    venue_city = fixture['fixture']['venue']['city']

    league_id = fixture['league']['id']
    league_name = fixture['league']['name']
    league_country = fixture['league']['country']
    league_logo = fixture['league']['logo']
    league_flag = fixture['league']['flag']
    league_round = fixture['league']['round']

    home_team_id = fixture['teams']['home']['id']
    home_team_name = fixture['teams']['home']['name']
    home_team_logo = fixture['teams']['home']['logo']
    away_team_id = fixture['teams']['away']['id']
    away_team_name = fixture['teams']['away']['name']
    away_team_logo = fixture['teams']['away']['logo']
    betting_odds_list = []
    if odds[0]:
        betting_odds_list = betting_odds.get_betting_odds_for_fixture(odds[1], fixture_id)
    else:
        betting_odds_list = []

    fixture_json = {"fixture_id": fixture_id,
                    "fixture_status": fixture_status,
                    "league_id": league_id,
                    "league_name": league_name,
                    "league_country": league_country,
                    "league_logo": league_logo,
                    "league_flag": league_flag,
                    "league_attr": league_attr,
                    "fixture_time": get_date_time_split(fixture_date)[1],
                    "fixture_date": get_date_time_split(fixture_date)[0],
                    "round": league_round,
                    "location": f"{venue_name}, {venue_city}",
                    "home_name": home_team_name,
                    "home_id": home_team_id,
                    "home_logo": home_team_logo,
                    "away_name": away_team_name,
                    "away_id": away_team_id,
                    "away_logo": away_team_logo,
                    "odds": betting_odds_list}
    return fixture_json


def get_date_time_split(date):
    date = datetime.fromisoformat(date)
    match_time = date.strftime("%H:%M:%S")
    match_date = date.strftime("%Y-%m-%d")
    return match_date, match_time


def save_upcoming_fixtures(date_string, fixture_list):
    count = mg.count_documents("upcoming_fixtures", {"date": date_string})
    daily_fixture = {
        "date": date_string,
        "fixtures": fixture_list
    }
    if count == 0:
        mg.add_record("upcoming_fixtures", daily_fixture)
    else:
        mg.update_record("upcoming_fixtures", {"date": date_string}, daily_fixture)


def check_when_last_team_fixtures_updated(team_id):
    """
    Check when the teams fixtures were last updated
    :param team_id: int
    :return: Boolean
    """
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


def add_previous_matches(team_id):
    resp = teams.update_teams_previous_matches(team_id, 20)
    try:
        team_name = mg.get_single_info("teams", {"id": team_id})
        return resp, team_name['name']
    except TypeError:
        new_team = teams.add_one_team(team_id)
        team_name = {}
        while new_team < 1:
            team_name = mg.get_single_info("teams", {"id": team_id})
            new_team = mg.count_documents("teams", {"id": team_id})
        return resp, team_name
    except KeyError:
        new_team = teams.add_one_team(team_id)
        while new_team < 1:
            new_team = mg.count_documents("teams", {"id": team_id})
        team_name = mg.get_single_info("teams", {"id": team_id})
        return resp, team_name['name']


def get_fixture_statistics(fixture_id, league_id):
    if check_if_league_has_statistics(league_id):
        querystring = {"fixture": fixture_id}
        stat_response = api.get_request(matches_url + "/statistics", querystring)
        json_response = json.loads(stat_response)
        total = json_response['results']
        if total > 0 and len(json_response['response'][0]) > 0:
            home_fixture_stats = json_response['response'][0]
            home_team_stats = {
                "team_id": home_fixture_stats['team']['id'],
                "team_name": home_fixture_stats['team']['name'],
                "statistics": create_statistics_json(home_fixture_stats['statistics'])
            }
        else:
            home_team_stats = {}

        if total > 0 and len(json_response['response'][1]) > 0:
            away_fixture_stats = json_response['response'][1]
            away_team_stats = {
                "team_id": away_fixture_stats['team']['id'],
                "team_name": away_fixture_stats['team']['name'],
                "statistics": create_statistics_json(away_fixture_stats['statistics'])
            }
        else:
            away_team_stats = {}
    else:
        home_team_stats = {}
        away_team_stats = {}

    return home_team_stats, away_team_stats


def create_statistics_json(stat_array):
    fixture_json = {}
    for x in stat_array:
        fixture_json.update({x['type']: x['value']})
    return fixture_json


def get_list_of_main_fixture_ids(fixtures):
    fixture_id_list = []
    main_leagues = leagues.get_all_main_leagues()
    for fixture in fixtures:
        if fixture['league']['id'] in main_leagues[1]:
            fixture_id_list.append(fixture['league']['id'])
    return fixture_id_list


def get_fixture_events(fixture_id, league_id):
    querystring = {"fixture": fixture_id}
    if check_if_league_has_events(league_id):
        event_response = api.get_request(matches_url + "/events", querystring)
        json_response = json.loads(event_response)
        total = json_response['results']

        if total > 0:
            return json_response['response']
        else:
            return None
    else:
        return None


def get_h2h_matches(home_team_id, away_team_id):
    querystring = {"h2h": f"{home_team_id}-{away_team_id}", "status": "FT"}
    h2h_response = api.get_request(matches_url + "/headtohead", querystring)
    response = json.loads(h2h_response)
    no_matches_added = 0
    fixtures = response['response']
    for x in fixtures:
        fixture_id = x['fixture']['id']
        league_id = x['league']['id']
        if not mg.document_exists("fixtures", {"id": fixture_id}):
            home_stats, away_stats = get_fixture_statistics(fixture_id, league_id)
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
                "events": get_fixture_events(fixture_id, league_id),
                "statistics_home": home_stats,
                "statistics_away": away_stats,
            }
            mg.add_record("fixtures", fixture)
            no_matches_added += 1
    return no_matches_added


def get_all_h2h_matches(home_team_id, away_team_id):
    query = {"team_ids": {"$all": [home_team_id, away_team_id]}}
    if not mg.document_exists("h2h_fixtures", query) or \
            mg.check_last_updated("h2h_fixtures", query) > timedelta(hours=2):
        querystring = {"h2h": f"{home_team_id}-{away_team_id}", "status": "FT"}
        h2h_response = api.get_request(matches_url + "/headtohead", querystring)
        response = json.loads(h2h_response)
        fixtures = response['response']
        if not mg.document_exists("h2h_fixtures", query):
            h2h_fixture_list = []
            for x in fixtures:
                fixture = build_h2h_fixture_list(x)
                h2h_fixture_list.append(fixture)

            h2h_entry = {
                "team_ids": (home_team_id, away_team_id),
                "fixtures": h2h_fixture_list,
                "last_updated": datetime.utcnow()
            }
            mg.add_record("h2h_fixtures", h2h_entry)
            return h2h_fixture_list
        else:
            h2h_record = mg.get_single_info("h2h_fixtures", query)
            previous_h2h_fixtures = h2h_record['fixtures']
            if len(previous_h2h_fixtures) != len(fixtures):
                h2h_fixture_list = []
                for x in fixtures:
                    fixture = build_h2h_fixture_list(x)
                    h2h_fixture_list.append(fixture)
                mg.update_one_record("h2h_fixtures", {"team_ids": {"$all": [home_team_id, away_team_id]}},
                                     {"$set": {"fixtures": h2h_fixture_list, "last_updated": datetime.utcnow()}})
                return h2h_fixture_list
            else:
                mg.update_one_record("h2h_fixtures", {"team_ids": {"$all": [home_team_id, away_team_id]}},
                                     {"$set": {"last_updated": datetime.utcnow()}})
                return mg.get_single_info("h2h_fixtures", query)

    else:
        return mg.get_single_info("h2h_fixtures", query)


def build_h2h_fixture_list(fixture):
    fixture_object = {
        "id": fixture['fixture']['id'],
        "date": fixture['fixture']['date'],
        "timestamp": fixture['fixture']['timestamp'],
        "venue": fixture['fixture']['venue'],
        "league_id": fixture['league']['id'],
        "league_name": fixture['league']['name'],
        "league_country": fixture['league']['country'],
        "league_logo": fixture['league']['logo'],
        "league_flag": fixture['league']['flag'],
        "league_season": fixture['league']['season'],
        "league_round": fixture['league']['round'],
        "home_id": fixture['teams']['home']['id'],
        "home_name": fixture['teams']['home']['name'],
        "home_logo": fixture['teams']['home']['logo'],
        "away_id": fixture['teams']['away']['id'],
        "away_name": fixture['teams']['away']['name'],
        "away_logo": fixture['teams']['away']['logo'],
        "goals_home": fixture['goals']['home'],
        "goals_away": fixture['goals']['away'],
        "score": fixture['score']
    }
    return fixture_object


def get_last_x_home_matches(team_id, num):
    query = {"home_id": {"$eq": team_id}}
    all_team_fixtures = mg.get_multiple_info("fixtures", query)
    sorted_fixtures = sorted(all_team_fixtures, key=lambda y: y['date'], reverse=True)
    team_fixtures = []
    for x in sorted_fixtures[:num]:
        team_fixtures.append(x)
    return sorted(team_fixtures, key=lambda y: y['date'], reverse=True)


def get_last_x_away_matches(team_id, num):
    query = {"away_id": {"$eq": team_id}}
    all_team_fixtures = mg.get_multiple_info("fixtures", query)
    sorted_fixtures = sorted(all_team_fixtures, key=lambda y: y['date'], reverse=True)
    team_fixtures = []
    for x in sorted_fixtures[:num]:
        team_fixtures.append(x)
    return sorted(team_fixtures, key=lambda y: y['date'], reverse=True)


def get_all_leagues_playing_for_date(fixture_date):
    #converted_date = parser.parse(fixture_date)
    filtered_date = fixture_date.strftime('%Y-%m-%d')
    querystring = {"date": filtered_date}
    if mg.document_exists("upcoming_fixtures", querystring):
        fixtures = mg.get_single_info("upcoming_fixtures", querystring)
    else:
        fixtures = get_fixtures_by_date(fixture_date, True)
    league_id_list = []
    for fixture in fixtures['fixtures']:
        if leagues.check_if_league(fixture['league_id']):
            league_id_list.append(fixture['league_id'])
    set_leagues = set(league_id_list)
    list_league_objects = []
    for x in set_leagues:
            list_league_objects.append(leagues.get_league_info_by_id(x))
    return list_league_objects
