import json
import re

import requests
from pydantic import BaseModel

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


# bearer
# https://abs.twimg.com/responsive-web/client-web/main.d71402aa.js
# auth_token
# https://api.twitter.com/1.1/onboarding/task.json
# csrf Set-Cookie
# https://twitter.com/i/api/graphql/qevmDaYaF66EOtboiNoQbQ/Viewer?variables=%7B%22withCommunitiesMemberships%22%3Atrue%7D&features=%7B%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D&fieldToggles=%7B%22isDelegate%22%3Afalse%2C%22withAuxiliaryUserLabels%22%3Afalse%7D


def post_body(session: requests.Session, body: BaseModel, token: str, link: str):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': f'Bearer {token}',
        'Cache-Control': 'no-cache',
        'Content-Length': '1617',
        'Content-Type': 'application/json',
        'Cookie': 'guest_id=v1%3A169597418127022288; g_state={"i_l":0}; kdt=pKSGOiGDX0ua2aZNql65nMYmNINZoEoZZzZ2IIic; auth_token=53bf0c708d4a9491fc67c3a45fabc2e4e915b2d3; ct0=e05983f97d92304914f42b8bf1b373e3586319f3bc07360db40d271e0cf0615944137509d9d2d1124f600156eedc3b86e61148e225e8f9c21468273ab45725eab521dde041940f565928c85fbd206cf8; lang=en; twid=u%3D1707665780618260480; dnt=1; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCEOcb%252BGKAToMY3NyZl9p%250AZCIlMzAxYmJiZWRjZTdiMDhlNzYyMjU3ZjFkMDRiODI5YzU6B2lkIiU4ZDMz%250AOWZjMGZhODNlNGVjMzNiMTAyYjQzMDFjOWQyZg%253D%253D--565dc36c55aad8c4fb00b4963a37c56b66a60828',
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
        'X-Client-Transaction-Id': 'uu2W0JWEJrh1GXSRNmp5N7FGHVJMkFTjd58SSMG6pChuAdPkke5yBiGmAogOOzBCt087fbq81MZD4HEVndoxINVQtCHIuw',
        'X-Csrf-Token': 'e05983f97d92304914f42b8bf1b373e3586319f3bc07360db40d271e0cf0615944137509d9d2d1124f600156eedc3b86e61148e225e8f9c21468273ab45725eab521dde041940f565928c85fbd206cf8',
        'X-Twitter-Active-User': 'yes',
        'X-Twitter-Auth-Type': 'OAuth2Session',
        'X-Twitter-Client-Language': 'en',
    }
    return session.post(link, headers=headers, json=body.model_dump_json())


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
