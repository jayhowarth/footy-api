import json
from datetime import datetime, timezone, timedelta

import leagues
from api_manager import APIManager as api
import mongo as mg

league_table_url = "https://api-football-v1.p.rapidapi.com/v3/standings"
current_season = datetime.today().strftime("%Y")


def update_all_league_tables():
    leagues_updated = []
    all_leagues = mg.get_multiple_info("leagues")
    added = False
    for x in all_leagues:
        check = check_current_season_and_standings(x)
        if check["standings"] is True and check["is_current"] is True:
            added = update_league_standings_by_league(x['id'])
        if added:
            leagues_updated.append({"League": x['name'], "Country": x['country_name']})
    if len(leagues_updated) > 0:
        return leagues_updated
    else:
        return "No teams added"


def update_league_standings_by_league(league_id):
    league_updated = False
    if leagues.check_if_league(league_id):
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


def all_teams_in_league(league_id):
    count = mg.count_documents("standings", {"id": league_id})
    time_delta = mg.check_last_updated("standings", {"id": league_id})
    if time_delta > timedelta(hours=12) or count == 0 or count is None:
        update_league_standings_by_league(league_id)
    league = mg.get_single_info("standings", {"id": league_id})
    standings = league['standings']
    return standings


def check_current_season_and_standings(data):
    has_standings = False
    is_current = False
    for x in data["league_seasons"]:
        if x["current"] is True:
            is_current = True
            if x["coverage"]["standings"] is True:
                has_standings = True
    return {"standings": has_standings, "is_current": is_current}