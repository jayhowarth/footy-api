import json
from api_manager import APIManager as api
import mongo as mg
from datetime import datetime, timedelta


league_table_url = "https://api-football-v1.p.rapidapi.com/v3/standings"
current_season = datetime.today().strftime("%Y")


def add_leagues():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    querystring = {}
    response = api.get_request(url, querystring)
    json_response = json.loads(response)
    total_countries = json_response['results']
    all_leagues = json_response['response']
    no_added = 0
    for x in all_leagues:
        league_id = x['league']['id']
        league_name = x['league']['name']
        league_type = x['league']['type']
        league_logo = x['league']['logo']
        league_country_name = x['country']['name']
        league_country_code = x['country']['code']
        league_country_flag = x['country']['flag']
        league_seasons = x['seasons']
        has_statistics = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['statistics_fixtures']
        has_events = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['events']
        has_lineups = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['lineups']
        has_player_stats = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['statistics_players']
        has_standings = x['seasons'][len(league_seasons) - 1]['coverage']['standings']
        has_players = x['seasons'][len(league_seasons) - 1]['coverage']['players']
        has_top_scorers = x['seasons'][len(league_seasons) - 1]['coverage']['top_scorers']
        has_top_assists = x['seasons'][len(league_seasons) - 1]['coverage']['top_assists']
        has_top_cards = x['seasons'][len(league_seasons) - 1]['coverage']['top_cards']
        has_injuries = x['seasons'][len(league_seasons) - 1]['coverage']['injuries']
        has_predictions = x['seasons'][len(league_seasons) - 1]['coverage']['predictions']
        has_odds = x['seasons'][len(league_seasons) - 1]['coverage']['odds']

        league = {
            "id": league_id,
            "name": league_name,
            "type": league_type,
            "logo": league_logo,
            "country_name": league_country_name,
            "country_code": league_country_code,
            "country_flag": league_country_flag,
            "league_seasons": league_seasons,
            "last_updated": datetime.utcnow(),
            "has_statistics": has_statistics,
            "has_events": has_events,
            "has_lineups": has_lineups,
            "has_player_stats": has_player_stats,
            "standings": has_standings,
            "players": has_players,
            "top_scorers": has_top_scorers,
            "top_assists": has_top_assists,
            "top_cards": has_top_cards,
            "injuries": has_injuries,
            "predictions": has_predictions,
            "odds": has_odds
        }
        count = mg.count_documents("leagues", {"id": league_id})
        if count == 0 or count is None:
            mg.add_record("leagues", league)
            no_added += 1

    return f'{no_added} Leagues'


def update_leagues():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    querystring = {}
    response = api.get_request(url, querystring)
    json_response = json.loads(response)
    total_countries = json_response['results']
    all_leagues = json_response['response']
    no_added = 0
    no_updated = 0
    for x in all_leagues:
        league_id = x['league']['id']
        league_name = x['league']['name']
        league_type = x['league']['type']
        league_logo = x['league']['logo']
        league_country_name = x['country']['name']
        league_country_code = x['country']['code']
        league_country_flag = x['country']['flag']
        league_seasons = x['seasons']
        has_statistics = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['statistics_fixtures']
        has_events = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['events']
        has_lineups = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['lineups']
        has_player_stats = x['seasons'][len(league_seasons) - 1]['coverage']['fixtures']['statistics_players']
        has_standings = x['seasons'][len(league_seasons) - 1]['coverage']['standings']
        has_players = x['seasons'][len(league_seasons) - 1]['coverage']['players']
        has_top_scorers = x['seasons'][len(league_seasons) - 1]['coverage']['top_scorers']
        has_top_assists = x['seasons'][len(league_seasons) - 1]['coverage']['top_assists']
        has_top_cards = x['seasons'][len(league_seasons) - 1]['coverage']['top_cards']
        has_injuries = x['seasons'][len(league_seasons) - 1]['coverage']['injuries']
        has_predictions = x['seasons'][len(league_seasons) - 1]['coverage']['predictions']
        has_odds = x['seasons'][len(league_seasons) - 1]['coverage']['odds']
        is_current = x['seasons'][len(league_seasons) - 1]['current']
        league = {
            "id": league_id,
            "name": league_name,
            "type": league_type,
            "logo": league_logo,
            "country_name": league_country_name,
            "country_code": league_country_code,
            "country_flag": league_country_flag,
            "league_seasons": league_seasons,
            "last_updated": datetime.utcnow(),
            "has_statistics": has_statistics,
            "has_events": has_events,
            "has_lineups": has_lineups,
            "has_player_stats": has_player_stats,
            "standings": has_standings,
            "players": has_players,
            "top_scorers": has_top_scorers,
            "top_assists": has_top_assists,
            "top_cards": has_top_cards,
            "injuries": has_injuries,
            "predictions": has_predictions,
            "odds": has_odds
        }
        count = mg.count_documents("leagues", {"id": league_id})
        if is_current:
            if count == 0 or count is None:
                mg.add_record("leagues", league)
                no_added += 1
            else:
                mg.update_record("leagues", {"id": league_id}, league)
                no_updated += 1

    return f'added {no_added} Leagues, updated {no_updated} leagues'


def get_league_info_by_id(league_id):
    """
    Gets leagues info from the league id
    :param league_id:
    :return: object of shape MainLeague
    """
    league = mg.get_single_info("leagues", {"id": league_id})
    return {"id": league_id,
            "name": league['name'],
            "country": league['country_name']
            }


def check_if_league(league_id):
    league = mg.get_single_info("leagues", {"id": league_id})
    try:
        if league['type'] == 'League':
            return True
        else:
            return False
    except TypeError:
        return False


def check_league_attributes(league_id):
    league = mg.get_single_info("leagues", {"id": league_id})
    try:
        attributes = {
            "has_events": league['has_events'],
            "has_lineups": league['has_lineups'],
            "has_player_stats": league['has_player_stats'],
            "has_statistics": league['has_statistics'],
            "has_injuries": league['injuries'],
            "has_odds": league['odds'],
            "has_players": league['players'],
            "has_predictions": league['predictions'],
            "has_standings": league['standings'],
            "has_assists": league['top_assists'],
            "has_cards": league['top_cards'],
            "has_scorers": league['top_scorers']
        }
    except TypeError:
        attributes = {
            "has_events": False,
            "has_lineups": False,
            "has_player_stats": False,
            "has_statistics": False,
            "has_injuries": False,
            "has_odds": False,
            "has_players": False,
            "has_predictions": False,
            "has_standings": False,
            "has_assists": False,
            "has_cards": False,
            "has_scorers": False
        }

    return attributes


def get_all_main_leagues():
    main_league_list = []
    main_league_list_ids = []
    main_leagues = mg.get_multiple_info("leagues", {"is_main": True})
    for league in main_leagues:
        main_league_list.append({
            "id": league['id'],
            "name": league['name'],
            "country": league['country_name']
        })
        main_league_list_ids.append(league['id'])
    return main_league_list, main_league_list_ids


def get_all_alternate_leagues():
    alt_league_list = []
    alt_league_list_ids = []
    main_leagues = mg.get_multiple_info("leagues", {"is_alt": True})
    for league in main_leagues:
        alt_league_list.append({
            "id": league['id'],
            "name": league['name'],
            "country": league['country_name']
        })
        alt_league_list_ids.append(league['id'])
    return alt_league_list, alt_league_list_ids


def check_diff_fixture_main_leagues(date_string):
    querystring = {"date": date_string}
    current_fixtures = mg.get_single_info("upcoming_fixtures", querystring)
    diff_a = []
    diff_b = []
    for fix in current_fixtures:
        diff_a.append(fix['league_id'])
    diff_b = get_all_main_leagues()[0]

    if len(diff_b) != len(set(diff_a)):
        mg.delete_one_record("upcoming_fixtures", querystring)
        return False
    else:
        return True


def update_main_leagues(league_id, is_main):
    """
    Patches league to set is_main to Boolean
    :param league_id: int
    :param is_main: Boolean
    :return: String of updated league
    """
    if mg.count_documents("leagues", {"id": league_id}) != 0:
        if mg.check_if_league_in_main({"id": league_id}) and not is_main:
            mg.update_one_record("leagues", {"id": league_id}, {"$set": {"is_main": is_main}})
            league_added = get_league_info_by_id(league_id)
            return f"Removed {league_added['name']} ({league_added['country']})"
        elif not mg.check_if_league_in_main({"id": league_id}) and is_main:
            mg.update_one_record("leagues", {"id": league_id}, {"$set": {"is_main": is_main}})
            league_added = get_league_info_by_id(league_id)
            return f"Added {league_added['name']} ({league_added['country']})"
        else:
            return "League already exists"
    else:
        return "League Does Not Exist"


def update_alternate_leagues(league_id, is_alt):
    """
    Patches league to set is_alt to Boolean
    :param league_id: int
    :param is_alt: Boolean
    :return: String of updated league
    """
    if mg.count_documents("leagues", {"id": league_id}) != 0:
        if mg.check_if_league_in_alternate({"id": league_id}) and not is_alt:
            mg.update_one_record("leagues", {"id": league_id}, {"$set": {"is_alt": is_alt}})
            league_added = get_league_info_by_id(league_id)
            return f"Removed {league_added['name']} ({league_added['country']})"
        elif not mg.check_if_league_in_alternate({"id": league_id}) and is_alt:
            mg.update_one_record("leagues", {"id": league_id}, {"$set": {"is_alt": is_alt}})
            league_added = get_league_info_by_id(league_id)
            return f"Added {league_added['name']} ({league_added['country']})"
        else:
            return "League already exists"
    else:
        return "League Does Not Exist"


def all_teams_in_league(league_id):
    count = mg.count_documents("standings", {"id": league_id})
    time_delta = mg.check_last_updated("standings", {"id": league_id})
    if time_delta > timedelta(hours=12) or count == 0 or count is None:
        update_league_standings_by_league(league_id)
    league = mg.get_single_info("standings", {"id": league_id})
    standings = league['standings']
    return standings


def update_league_standings_by_league(league_id):
    league_updated = False
    count = mg.count_documents("standings", {"id": league_id})
    time_delta = mg.check_last_updated("standings", {"id": league_id})
    if time_delta > timedelta(hours=12) or count == 0 or count is None:
        querystring = {"league": league_id, "season": current_season}
        standings_response = api.get_request(league_table_url, querystring)
        json_response = json.loads(standings_response)
        total = json_response['results']
        standings = json_response['response']

        if total > 0:
            for x in standings:
                standings_id = x["league"]["id"]
                all_standings = {
                    "id": standings_id,
                    "name": x["league"]["name"],
                    "country": x["league"]["country"],
                    "logo": x["league"]["logo"],
                    "flag": x["league"]["flag"],
                    "season": x["league"]["season"],
                    "standings": x["league"]["standings"][0],
                    "last_updated": datetime.utcnow()
                    }
                if count == 0:
                    mg.add_record("standings", all_standings)
                    league_updated = True
                else:
                    mg.update_record("standings", {"id": standings_id}, all_standings)
                    league_updated = True
        else:
            league_updated = False
        return league_updated
    else:
        return league_updated


def check_if_league_has_events(league_id):
    league = mg.get_single_info("leagues", {"id": league_id})
    try:
        return league['has_events']
    except KeyError:
        return True
    except TypeError:
        return True


def check_if_league_has_statistics(league_id):
    league = mg.get_single_info("leagues", {"id": league_id})
    try:
        return league['has_statistics']
    except KeyError:
        return True
    except TypeError:
        return True


def get_league_standings_stats(team_id, league_id):
    standings = all_teams_in_league(league_id)
    try:
        for table in standings:
            for x in table:
                if x['team']['id'] == team_id:
                    return x, len(table)
    except TypeError:
        for x in standings:
            if x['team']['id'] == team_id:
                return x, len(x)


