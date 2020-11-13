import httpx
from enum import Enum


GET = 'GET'
POST = 'POST'


class EPublishedFileQueryType(Enum):
    RANKED_BY_VOTE = 0
    RANKED_BY_PUBLICATION_DATE = 1
    ACCEPTED_FOR_GAME_RANKED_BY_ACCEPTANCE_DATE = 2
    RANKED_BY_TREND = 3
    FAVORITED_BY_FRIENDS_RANKED_BY_PUBLICATION_DATE = 4
    CREATED_BY_FRIENDS_RANKED_BY_PUBLICATION_DATE = 5
    RANKED_BY_NUM_TIMES_REPORTED = 6
    CREATED_BY_FOLLOWED_USERS_RANKED_BY_PUBLICATION_DATE = 7
    NOT_YET_RATED = 8
    RANKED_BY_TOTAL_UNIQUE_SUBSCRIPTIONS = 9
    RANKED_BY_TOTAL_VOTES_ASC = 10
    RANKED_BY_VOTES_UP = 11
    RANKED_BY_TEXT_SEARCH = 12
    RANKED_BY_PLAYTIME_TREND = 13
    RANKED_BY_TOTAL_PLAYTIME = 14
    RANKED_BY_AVERAGE_PLAYTIME_TREND = 15
    RANKED_BY_LIFETIME_AVERAGE_PLAYTIME = 16
    RANKED_BY_PLAYTIME_SESSIONS_TREND = 17
    RANKED_BY_LIFETIME_PLAYTIME_SESSIONS = 18
    RANKED_BY_INAPPROPRIATE_CONTENT_RATING = 19


class SteamAPIClient:
    api_url = 'https://api.steampowered.com/'

    def __init__(self, api_key):
        self.client = httpx.AsyncClient()
        self.api_key = api_key
    
    async def request(self, endpoint, params={}, method=GET):
        params['key'] = self.api_key
        url = self.api_url + endpoint.lstrip('/')
        if method == 'GET':
            response = await self.client.get(url, params=params)
        elif method == 'POST':
            response = await self.client.post(url, data=params)
        else:
            raise ValueError(f"Request method {method} is neither GET or POST.")
        response.raise_for_status()
        return response.json()['response']
