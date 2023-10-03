import json
import re

import requests

from client.login import login
from client.schemas import HomeTimelineRequest, HomeTimelineResponse

PATH = {
    "HomeTimeline": '/i/api/graphql/{}/HomeTimeline',
}


def build_uri(name: str, ssl: bool = True, params=None):
    if params is None:
        params = {}
    proto = "https" if ssl else "http"
    host = "{}://{}".format(
        proto,
        'twitter.com'
    )

    query = "&".join(
        [
            "{}={}".format(k, v)
            for k, v in params.items()
        ]
    )
    if query != "":
        query = "?{}".format(query)

    return "".join([host, PATH[name], query])


class TwitterSession:
    _token: str
    _session: requests.Session

    def __init__(self, token: str, session: requests.Session):
        self._token = token
        self._session = session

    def get_home_timeline(self) -> HomeTimelineResponse:
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Authorization': f'Bearer {self._token}',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'Origin': 'https://twitter.com',
            'Pragma': 'no-cache',
            'Referer': 'https://twitter.com/home?lang=en',
            'Sec-Ch-Ua': '"Brave";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': 'Windows',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Gpc': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'X-Csrf-Token': self._session.cookies.get('ct0'),
            'X-Guest-Token': self._session.cookies.get('guest_token')
        }
        params = {  # standard params
            'variables': '{"count": 20, "includePromotedContent": true, "latestControlAvailable": true, '
                         '"requestContext": "launch", "withCommunity": true}',
            'features': '{"responsive_web_graphql_exclude_directive_enabled": true, "verified_phone_label_enabled": '
                        'false, "responsive_web_home_pinned_timelines_enabled": false, '
                        '"creator_subscriptions_tweet_preview_api_enabled": true, '
                        '"responsive_web_graphql_timeline_navigation_enabled": true, '
                        '"responsive_web_graphql_skip_user_profile_image_extensions_enabled": false, '
                        '"tweetypie_unmention_optimization_enabled": true, "responsive_web_edit_tweet_api_enabled": '
                        'true, "graphql_is_translatable_rweb_tweet_is_translatable_enabled": true, '
                        '"view_counts_everywhere_api_enabled": true, "longform_notetweets_consumption_enabled": true, '
                        '"responsive_web_twitter_article_tweet_consumption_enabled": false, '
                        '"tweet_awards_web_tipping_enabled": false, "freedom_of_speech_not_reach_fetch_enabled": '
                        'true, "standardized_nudges_misinfo": true, '
                        '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": true, '
                        '"longform_notetweets_rich_text_read_enabled": true, '
                        '"longform_notetweets_inline_media_enabled": true, '
                        '"responsive_web_media_download_video_enabled": false, '
                        '"responsive_web_enhance_cards_enabled": false} '
        }
        resp = self._session.get(
            build_uri("HomeTimeline", params=params).replace('{}', '-8TWbLqVU1ROq-eeErVc2w'),
            headers=headers
        )
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.reason)
            print(resp.text)
            raise Exception('Status code not 200')
        text = resp.text
        return HomeTimelineResponse(**json.loads(text))


class TwitterCredentials:
    _email: str
    _username: str
    _password: str

    def __init__(self, email: str, username: str, password: str):
        self._email = email
        self._username = username
        self._password = password

    def auth(self) -> TwitterSession:
        resp = requests.get('https://abs.twimg.com/responsive-web/client-web/main.d71402aa.js')
        search_results = re.search('\"Bearer ([a-zA-Z%0-9]+)\"', resp.text)
        if not search_results:
            raise Exception('Cant find Bearer token')
        bearer_token = search_results.group(1)
        if len(bearer_token) == 0:
            raise Exception('Cant find Bearer token')

        session = login(
            self._email,
            self._username,
            self._password,
            bearer_token)
        return TwitterSession(bearer_token, session)
