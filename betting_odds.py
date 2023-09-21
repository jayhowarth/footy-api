import mongo as mg
import json
from api_manager import APIManager as api
from datetime import datetime, date, timedelta

odds_url = 'https://api-football-v1.p.rapidapi.com/v3/odds'


def get_betting_odds_for_date(fixture_date, fixtures):
    #converted_date = fixture_date.strftime('%Y-%m-%d')
    today = datetime.today().strftime('%Y-%m-%d')
    if datetime.strptime(fixture_date, '%Y-%m-%d') >= datetime.strptime(today, '%Y-%m-%d'):
        if len(fixtures) > 0:
            querystring = {"date": fixture_date, "bookmaker": 8}

            init_resp = json.loads(api.get_request(odds_url, querystring))

            pages = init_resp['paging']['total']
            odds_list = []
            for page in range(1, int(pages)):
                if page == 1:
                    response = init_resp
                else:
                    querystring = {"date": fixture_date, "page": str(page), "bookmaker": "8"}
                    response = json.loads(api.get_request(odds_url, querystring))

                for x in response['response']:
                    if x['league']['id'] in fixtures:
                        odds_list.append({
                            "fixture": x['fixture']['id'],
                            "date": x['fixture']['date'],
                            "bookmaker_id": x['bookmakers'][0]['id'],
                            "bookmaker": x['bookmakers'][0]['name'],
                            "updated": x['update'],
                            "bets": x['bookmakers'][0]['bets']
                        })
            return True, odds_list
        else:
            return False, "No Fixtures"
    else:
        return False, "Fixtures Played"


def get_betting_odds_for_fixture(betting_fixture_list, fixture_id):
    if len(betting_fixture_list) > 0:
        for fixture in betting_fixture_list:
            if fixture['fixture'] == fixture_id:
                return fixture['bets']
    else:
        return []

def upcoming_fixtures_has_odds(the_date):
    filtered_date = the_date.strftime('%Y-%m-%d')
    querystring = {"date": filtered_date}
    exists = mg.document_exists("upcoming_fixtures", querystring)
    is_future = the_date.day >= datetime.today().day
    if exists and is_future:
        fixture_document = mg.get_single_info("upcoming_fixtures", querystring)
        if "odds" in fixture_document['fixtures'][0]:
            return True
        else:
            mg.delete_one_record("upcoming_fixtures", querystring)
            return False
    else:
        return False


