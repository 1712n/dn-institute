import calendar
import os
from datetime import datetime
from urllib.parse import urlparse
from uuid import uuid4

from bson import Binary, UuidRepresentation
from dotenv import dotenv_values
from pymongo import MongoClient

from client import TwitterCredentials
from client.schemas import EntryContract, MediaItemContract
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
        source=source
    ).model_dump()


if __name__ == '__main__':
    mongodb_client = MongoClient(config["ATLAS_URI"], uuidRepresentation='standard')
    database = mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")
    response = TwitterCredentials(config["TWITTER_EMAIL"], config["TWITTER_USERNAME"], config["TWITTER_PASSWORD"]) \
        .auth().get_home_timeline()
    tweets = list(
        map(
            map_home_timeline_entry_to_tweet_model,
            filter(
                lambda x: x is not None and
                          x.content is not None and
                          x.content.item_content is not None and
                          x.content.item_content.tweet_results is not None and
                          x.content.item_content.tweet_results.result is not None and
                          x.content.item_content.tweet_results.result.legacy is not None,
                response.data.home.home_timeline_urt.instructions[0].entries
            )
        )
    )
    database["twitter_test"].insert_many(tweets)
    print('Scraped')
