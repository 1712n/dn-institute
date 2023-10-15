import calendar
import os
from datetime import datetime
from typing import Optional, Any, Set, Mapping
from urllib.parse import urlparse
from uuid import uuid4

from bson import Binary, UuidRepresentation
from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import BulkWriteError, ConnectionFailure

from client import TwitterCredentials
from client.schemas import EntryContract, MediaItemContract, HomeTimelineResponse
from models import TweetModel, MessageModel, MediaItemModel, UserModel, SourceModel, ChannelModel, ReferencedPostModel, \
    Polygon

config = dotenv_values(".env")


def map_media_item_to_media_item_model(item: MediaItemContract):
    if item.type == 'photo':
        type = 'image'
    elif item.type == 'video':
        type = 'video'
    elif item.type == 'audio':
        type = 'audio'
    else:
        type = 'image'
    return MediaItemModel(
        id=item.id_str,
        type=type,
        title=item.display_url,
        file_name=os.path.basename(urlparse(item.media_url_https).path),
        url=item.media_url_https
    )


def map_home_timeline_entry_to_tweet_model(entry: EntryContract):
    legacy = entry.content.item_content.tweet_results.result.legacy
    media = filter(
        lambda x:
        x[0] is not None and x[0] == 'media',
        map(
            lambda xxx: xxx.entries,
            filter(
                lambda xy: xy is not None,
                legacy
            )
        )
    )
    media = [] if media is None else [
        i for ml in map(
            lambda y: list(
                map(
                    map_media_item_to_media_item_model,
                    y[1]
                )
            ),
            filter(
                lambda x:
                x[0] is not None and x[1] is not None and x[0] == 'media',
                legacy.entities
            )
        ) for i in ml
    ]
    message = MessageModel(
        id=entry.content.item_content.tweet_results.result.rest_id,
        text=legacy.full_text,
        language=legacy.lang,
        enrichment='',
        media=media
    )
    user_results_result = entry.content.item_content.tweet_results.result.core.user_results.result
    user = UserModel(
        id=user_results_result.rest_id,
        name=user_results_result.legacy.name
    )
    channel = ChannelModel(
        id=user_results_result.rest_id,
        name=user_results_result.legacy.name
    )
    if legacy.quoted_status_id_str is None:
        referenced_post = None
        source_specific_fields = None
    else:
        quoted_status_permalink = legacy.quoted_status_permalink
        referenced_post = ReferencedPostModel(
            id=legacy.quoted_status_id_str,
            url=quoted_status_permalink.expanded,
        )
        source_specific_fields = {
            'url': quoted_status_permalink.url,
            'display': quoted_status_permalink.display
        }
    if legacy.place is not None:
        bounding_box = legacy.place.bounding_box
        if bounding_box.type.lower() == 'polygon':
            geo_coords = Polygon(
                bbox=bounding_box.coordinates[0][0],
                coordinates=bounding_box.coordinates
            )
        else:
            geo_coords = None
    else:
        geo_coords = None

    source = SourceModel(
        platform='Twitter',
        channel=channel,
        referenced_post=referenced_post,
        source_specific_fields=source_specific_fields
    )
    explicit_binary = Binary.from_uuid(uuid4(), UuidRepresentation.STANDARD)
    return TweetModel(
        id=explicit_binary,
        timestamp=calendar.timegm(
            datetime.strptime(
                legacy.created_at,
                '%a %b %d %H:%M:%S %z %Y'
            ).timetuple()
        ),
        message=message,
        user=user,
        geo_coords=geo_coords,
        source=source,
        schema_version='1'
    ).model_dump()


def connect_to_database() -> Optional[Database[Mapping[str, Any]]]:
    try:
        mongodb_client = MongoClient(config["ATLAS_URI"], uuidRepresentation='standard')
    except ConnectionFailure as error:
        print(f"Could not connect to server: {error}")
        return None
    return mongodb_client[config["DB_NAME"]]

def get_response() -> Optional[HomeTimelineResponse]:
    try:
        return TwitterCredentials(config["TWITTER_EMAIL"], config["TWITTER_USERNAME"], config["TWITTER_PASSWORD"]) \
            .auth().get_home_timeline()
    except Exception as exception:
        print(exception)
        return None


def home_timeline_to_database_tweets(home_timeline_response: HomeTimelineResponse) -> list[dict[str, Any]]:
    return list(
        map(
            map_home_timeline_entry_to_tweet_model,
            filter(
                lambda x: x is not None and
                          x.content is not None and
                          x.content.item_content is not None and
                          x.content.item_content.tweet_results is not None and
                          x.content.item_content.tweet_results.result is not None and
                          x.content.item_content.tweet_results.result.legacy is not None,
                home_timeline_response.data.home.home_timeline_urt.instructions[0].entries
            )
        )
    )


def get_existing_message_ids(tweets_list: list[dict[str, Any]]) -> Set[str]:
    try:
        cursor = database["twitter_test"].find(
            {
                'message.id': {
                    "$in": list(map(lambda x: x['message']['id'], tweets_list))
                }
            },
            {
                "_id": 0,
                "message.id": 1
            }
        )
        return set(map(lambda x: x['message']['id'], list(cursor)))
    except TypeError as error:
        print(f'Error on fetching existing tweets: {error}')


if __name__ == '__main__':
    database = connect_to_database()
    if database is not None:
        print("Connected to the MongoDB database!")

        response = get_response()
        if response is not None:
            tweets = home_timeline_to_database_tweets(response)
            existing_ids = get_existing_message_ids(tweets)
            print(f'{len(existing_ids)} tweets is already exists')
            tweets = list(
                filter(
                    lambda x: x['message']['id'] not in existing_ids,
                    tweets
                )
            )
            print(f'Skipping tweets with ids: {existing_ids}')
            try:
                database["twitter_test"].insert_many(tweets, ordered=False)
            except BulkWriteError as err:
                print(f'Error on inserting tweets: {err}')
            print('Scraped')
        else:
            print('Response is None')
            print('NOT Scraped')
    else:
        print('NOT Scraped')
