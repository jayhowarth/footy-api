import requests
from redis_manager import RedisManager as r


class APIManager:
    def __init__(self, url, context):
        self._response = None

        self.url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        self.context = context
        self.headers = {
            "X-RapidAPI-Key": "8c50f45cb9msh5b6eb0932e414eep170ed9jsnf9241a97be15",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
             }

    @staticmethod
    def get_request(url, querystring):
        headers = {
            "X-RapidAPI-Key": "8c50f45cb9msh5b6eb0932e414eep170ed9jsnf9241a97be15",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        try:
            req_remaining = response.headers['X-RateLimit-requests-Remaining']
            r.set_remaining_counter(req_remaining)
            if int(req_remaining) < 5:
                print('Remaining: ' + r.get_remaining_counter())
                return {"results": 0}
            else:
                return response.text
        except KeyError:
            print('Key Error in header')


