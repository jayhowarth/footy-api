import json
from typing import Union

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import mongo as mg

import leagues
# import stat_calculator
# from task import update_selected_league_tables, update_all_previous_matches_for_league
import task
import teams
from leagues import update_main_leagues, update_alternate_leagues, get_league_info_by_id, get_all_main_leagues
from betting_odds import get_betting_odds_for_date
from standings import update_league_standings_by_league
from calculator.payload_generator import analyse_fixture, get_top_results
import fixtures

from datetime import datetime, date, timedelta

app = FastAPI()

league_list = [39, 40, 41, 42, 43, 45, 48,
               135, 136, 137, 140, 141, 143, 61, 62, 66, 88,
               89, 78, 79, 80, 94, 97,
               103, 104, 113, 114, 115, 119, 120, 144, 145, 147, 179,
               180, 181, 182, 183, 184, 185, 207, 208, 218, 219]

fixtures_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"


class Fixtures(BaseModel):
    date: date
    is_main: bool


class MainLeague(BaseModel):
    id: int
    name: str
    country: str


@app.get("/")
async def root():
    """
    Welcome message
    :return: String
    """
    return {"message": "Welcome to Footy Stats"}


@app.get("/api/get_league/{league_id}")
async def get_league(league_id):
    """
    Retrieves League Info from league id
    :param league_id: int
    :return: League Info in json
    """
    league_info = get_league_info_by_id(int(league_id))
    return league_info


@app.get("/api/main_leagues")
async def get_main_leagues():
    return get_all_main_leagues()


@app.patch("/api/main_leagues/{league_id}")
async def update_main_league(league_id: int):
    """
    Updates/Adds the is_main values for single league
    :param league_id: int
    :return: Boolean
    """
    if league_id > 0:
        is_main = True
    else:
        is_main = False
    response = update_main_leagues(abs(league_id), is_main)
    return response


@app.patch("/api/alt_leagues/{league_id}")
async def update_alternate_league(league_id: int):
    """
    Updates/Adds the is_main values for single league
    :param league_id: int
    :return: Boolean
    """
    if league_id > 0:
        is_alt = True
    else:
        is_alt = False
    response = update_alternate_leagues(abs(league_id), is_alt)
    return response


@app.post("/api/fixtures")
async def get_fixtures(fix: Fixtures):
    """
    Return all fixtures for given date
    :param fix: Fixtures
    :return: all fixtures as Json list
    """
    # fixtures_date = f"{fix.date.strftime('%Y-%m-%d')}"
    return JSONResponse(fixtures.get_fixtures_by_date(fix.date, fix.is_main))


@app.get("/api/fixtures_odds")
async def get_fixtures_odds(fix: Fixtures):
    """
    Return all fixtures for given date
    :param fix: Fixtures
    :return: all fixtures as Json list
    """
    fixtures_date = f"{fix.date.strftime('%Y-%m-%d')}"
    fix = fixtures.get_fixtures_by_date(fix.date, fix.is_main)
    fix_list = fixtures.get_list_of_main_fixture_ids(fix)

    return JSONResponse(get_betting_odds_for_date(fixtures_date, fix_list))


@app.get("/api/fixture/{fixture}")
async def get_fixture(fixture: int):
    """
    Get a fixture by id
    :param fixture: fixture id
    :return: json of the fixture
    """
    return {"message": f"Hello {fixture}"}


@app.post("/api/update_tables")
async def update_tables(leagues_list: list[MainLeague]):
    """
    Updates the league tables
    :param leagues: list of league objects to update
    :return: Json of leagues updated
    """
    leagues_response = []
    for league in leagues_list:
        leagues_response.append(json.loads(league.model_dump_json()))
    task.update_selected_league_tables.delay(leagues_response)
    return leagues_response


@app.get("/api/update_league_table/{league}")
async def update_single_table(league):
    """
    Updates the league tables
    :param leagues: list of league objects to update
    :return: Json of leagues updated
    """
    update_league_standings_by_league(int(league))
    return f"Update {league} League"


@app.get("/api/update_league_tables")
async def update_tables():
    """
    Updates the league tables
    :param leagues: list of league objects to update
    :return: Json of leagues updated
    """
    main_leagues = leagues.get_all_main_leagues()
    alt_leagues = leagues.get_all_alternate_leagues()
    # main_leagues = main_leagues[0]
    # alt_leagues = alt_leagues[0]
    all_leagues = main_leagues[0] + alt_leagues[0]
    task.update_selected_league_tables.delay(all_leagues)
    return "Update All League Tables"


@app.post("/api/update_teams_in_league")
async def update_teams_previous_matches_in_league(main_leagues: MainLeague):
    """
    Updates teams within league
    :param main_leagues: object
    :return: list of teams updated
    """
    task.update_all_previous_matches_for_league.delay(main_leagues.id)
    return f"Updating {main_leagues.name}"


@app.get("/api/update_todays_fixtures")
async def update_teams_in_todays_fixtures(fix: Fixtures):
    """
    Updates teams within league
    :param main_leagues: object
    :return: list of teams updated
    """
    task.update_fixtures_for_date.delay(fix.date)
    return f"Updating fixtures for {fix.date}"


@app.get("/api/update_teams_leagues_for_date")
async def update_all_teams_previous_matches_in_league(fix: Fixtures):
    """
    Updates teams within league
    :param fix:
    :param main_leagues: object
    :return: list of teams updated
    """

    task.update_all_previous_matches_for_league_for_date.delay(fix.date)
    return f"Updating All Leagues for {fix.date}"


@app.get("/api/update_all_leagues")
async def update_all_leagues():
    """
    :return: No leagues added
    """
    return leagues.add_leagues()


@app.get("/api/update_all_teams")
async def update_all_team():
    """
    :return: No leagues added
    """
    task.update_all_teams.delay()
    return "Updating Teams"


@app.post("/api/update_all_teams_league")
async def update_all_teams_league(fix: Fixtures):
    task.update_all_teams_league.delay(fix.is_main)
    if fix.is_main:
        return "Updating Teams in Main Leagues"
    else:
        return "Updating All Teams"


@app.get("/api/generate_scores")
def generate_all_scores_for_date(fix: Fixtures):
    try:
        task.generate_scores_for_matches.delay(fix.date)
        return "Generating Scores"
    except task.generate_scores_for_matches.OpationalError as exc:
        print('celery error')


@app.get("/api/test")
async def test():
    """
    :return: No leagues added
    """
    # analyse_fixture(1044309, datetime.today())
    # fixtures.get_all_leagues_playing_for_date(datetime.today())
    # x = mg.get_all_records("teams")
    dd = datetime.strptime("2023-10-09", '%Y-%m-%d')
    res = analyse_fixture(980246, 473, dd)
    # res = get_top_results(dd)
    # teams.add_one_team(21595)
    return res
