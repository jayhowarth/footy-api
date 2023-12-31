import os
import time

import fixtures
import teams
from celery_config import app
from datetime import datetime
from dateutil import parser
import leagues, standings
from standings import update_league_standings_by_league
from leagues import get_league_info_by_id, \
    get_all_main_leagues, \
    all_teams_in_league
from fixtures import check_when_last_team_fixtures_updated, \
    add_previous_matches, \
    get_fixtures_by_date, \
    get_all_h2h_matches
from teams import check_when_last_team_fixtures_updated
from calculator.payload_generator import analyse_fixture
from redis_manager import RedisManager as r
import mongo as mg


@app.task
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")


@app.task
def update_all_teams():
    teams.update_all_teams_by_league()

@app.task
def update_selected_league_tables(leagues):
    for league in leagues:
        update_league_standings_by_league(int(league['id']))
        item = get_league_info_by_id(int(league['id']))
        print(f"Updated {item['name']} in {item['country']}")


@app.task
def update_all_previous_matches_for_league(league_id):
    standings = all_teams_in_league(league_id)
    total_added = 0
    for x in standings:
        needs_updating = check_when_last_team_fixtures_updated(x['team']['id'])
        if needs_updating:
            team = add_previous_matches(x['team']['id'])
            total_added += team[0]
        print('Remaining: ' + str(r.get_remaining_counter()))
        print(f"Updated matches for {x['team']['name']}")
    print(f'{total_added} total matches added')


@app.task
def update_all_previous_matches_for_league_for_date(fixture_date):
    leagues = fixtures.get_all_leagues_playing_for_date(fixture_date)
    for league in leagues:
        update_all_previous_matches_for_league(league['id'])
        print(f"Updated {league['name']} in {league['country']}")


@app.task
def update_previous_matches(all_fixtures):
    # all_fixtures = get_fixtures_by_date(fixture_date, True)
    total_added = 0
    home_added = 0
    away_added = 0
    h2h_added = 0
    total_fixtures = len(all_fixtures)
    for idx, x in enumerate(all_fixtures):
        home_updated = check_when_last_team_fixtures_updated(x['home_id'])
        away_updated = check_when_last_team_fixtures_updated(x['away_id'])
        if home_updated:
            home = add_previous_matches(x['home_id'])
            home_added = home[0]
        if away_updated:
            away = add_previous_matches(x['away_id'])
            away_added = away[0]
        if home_updated and away_updated:
            h2h_added = get_all_h2h_matches(x['home_id'], x['away_id'])
        total_added += (home_added + away_added)
        print('Remaining: ' + str(r.get_remaining_counter()))
        print(str(idx + 1) + ' of ' + str(total_fixtures) + ': ' + x['home_name'] + ' vs ' + x['away_name'])
    print(f'{total_added} total matches added')


@app.task
def update_h2h_for_todays_matches():
    all_fixtures = get_fixtures_by_date(datetime.now(), True)
    total_added = 0
    for idx, x in enumerate(all_fixtures):
        h2h_added = get_all_h2h_matches(x['home_id'], x['away_id'])
        print('Remaining: ' + str(r.get_remaining_counter()))
        total_added += h2h_added
    print(f'{total_added} total matches added')


@app.task
def update_all_teams_league(main_only):
    if main_only:
        main_leagues = leagues.get_all_main_leagues()[1]
        alt_leagues = leagues.get_all_alternate_leagues()[1]
        all_leagues = alt_leagues
        for league in all_leagues:
            if leagues.check_if_league(league):
                all_teams = standings.all_teams_in_league(league)
                try:
                    for sub_league in all_teams:
                        for team in sub_league:

                                teams.update_teams_league(team['team']['id'])
                                mg.update_one_record("teams", {"id": team['team']['id']},
                                                     {"$set": {"current_league_id": league,
                                                               "last_league_update": datetime.utcnow()}})
                                print(f"Updated {team['team']['name']}")
                except TypeError:
                    for team in all_teams:
                        teams.update_teams_league(team['team']['id'])
                        mg.update_one_record("teams", {"id": team['team']['id']},
                                             {"$set": {"current_league_id": league,
                                                       "last_league_update": datetime.utcnow()}})
                        print(f"Updated {team['team']['name']}")

                    print(f"Error in team {team}")
                    pass
            else:
                print("Not a league")

    else:
        all_teams = mg.get_all_records("teams")
        for team in all_teams:
            team_updated = teams.update_teams_league(team['id'])
            print(team_updated)


@app.task
def generate_scores_for_matches(fixture_date):
    filtered_date = fixture_date.strftime('%Y-%m-%d')
    querystring = {"date": filtered_date}
    if mg.document_exists("upcoming_fixtures", querystring):
        fix = mg.get_single_info("upcoming_fixtures", querystring)
    else:
        fix = get_fixtures_by_date(fixture_date, True)
    fixtures_list = []
    counter = 0
    for fixture in fix['fixtures']:
        counter += 1
        try:
            if "scores" in fixture:
                print(f"{fixture['home_name']} vs {fixture['away_name']} Exists")
            else:
                print(f"Starting fixture {counter}: {fixture['fixture_id']}")
                fixture['scores'] = analyse_fixture(fixture['fixture_id'], fixture['league_id'], fixture_date)
                fixtures_list.append(fixture)
                print(f"Added: {fixture['home_name']} vs {fixture['away_name']}")

        except KeyError:
            print(f"Starting fixture {counter}: {fixture['fixture_id']}")
            fixture['scores'] = analyse_fixture(fixture['fixture_id'], fixture['league_id'], fixture_date)
            fixtures_list.append(fixture)
            print(f"Added: {fixture['home_name']} vs {fixture['away_name']}")

    mg.update_one_record("upcoming_fixtures", querystring,
                         {"$set": {"fixtures": fixtures_list}})
    mg.update_one_record("upcoming_fixtures", querystring,
                         {"$set": {"complete": True}})

    return fixtures_list


@app.task
def update_fixtures_for_date(fixture_date):
    filtered_date = fixture_date.strftime('%Y-%m-%d')
    querystring = {"date": filtered_date}
    fixtures_exist = mg.document_exists("upcoming_fixtures", querystring)
    if fixtures_exist:
        try:
            complete = mg.get_single_info("upcoming_fixtures", querystring)['complete']
        except KeyError:
            complete = False
        if not complete:
            # Calculate scores
            generate_scores_for_matches(fixture_date)
            print("Generated Scores")
            time.sleep(5)
            return "Complete"
        else:
            print("Already Exists")
            pass
    else:
        # Get all fixtures and odds
        all_fixtures = get_fixtures_by_date(fixture_date, True)
        print("Updated Fixtures")
        time.sleep(5)
        # Update all teams previous fixtures
        update_previous_matches(all_fixtures)
        print("Updated Previous matches")
        time.sleep(5)
        generate_scores_for_matches(fixture_date)
        print("Generated Scores")
        time.sleep(5)
        return "Complete"


