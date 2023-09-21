from datetime import datetime

import mongo as mg
import json
from api_manager import APIManager as api
from leagues import all_teams_in_league

player_url = "https://api-football-v1.p.rapidapi.com/v3/players"

def update_all_players_in_league(league_id):
    teams = all_teams_in_league(league_id)
    for x in teams:
        update_all_players_in_squad(x['standings']['team']['id'])

def update_all_players_in_squad(team_id):
    querystring = {"team": team_id}
    squad_response = api.get_request(player_url + "/squads", querystring)
    json_response = json.loads(squad_response)
    total = json_response['results']
    no_players_added = 0
    no_players_updated = 0
    all_players = json_response['response'][0]['players']
    team_id = json_response['response'][0]['team']['id']
    team_name = json_response['response'][0]['team']['name']
    team_logo = json_response['response'][0]['team']['logo']
    for x in all_players:
        player_id = x['id']
        player = get_all_player_statistics(player_id)
        if not mg.document_exists("players", {"id": player_id}):
            mg.add_record("players", player)
            no_players_added += 1
        else:
            if check_if_difference_in_statistics(player_id, player["statistics"]):
                mg.update_record("players", {"id": player_id}, player)
    return f"{no_players_added} players added, {no_players_updated} players updated"


def get_all_player_statistics(player_id):
    querystring = {"id": player_id, "season": "2022"}
    player_response = api.get_request(player_url, querystring)
    json_response = json.loads(player_response)
    all_player_stats = json_response['response'][0]
    return {
        "id": all_player_stats['player']['id'],
        "name": all_player_stats['player']['name'],
        "firstname": all_player_stats['player']['firstname'],
        "lastname": all_player_stats['player']['lastname'],
        "age": all_player_stats['player']['age'],
        "birth_date": all_player_stats['player']['birth']['date'],
        "nationality": all_player_stats['player']['nationality'],
        "height": all_player_stats['player']['height'],
        "weight": all_player_stats['player']['weight'],
        "injured": all_player_stats['player']['injured'],
        "photo": all_player_stats['player']['photo'],
        "statistics": all_player_stats['statistics'],
        "last_updated": datetime.utcnow()
    }


def check_if_difference_in_statistics(player_id, new_stats):
    old_stats = mg.get_single_info("players", {"id": player_id})
    needs_updating = False
    if len(old_stats['statistics']) == len(new_stats):
        for x in range(len(new_stats)):
            if new_stats[x]['games']['appearences'] != (old_stats['statistics'][x]['games']['appearences']):
                needs_updating = True
    return needs_updating
