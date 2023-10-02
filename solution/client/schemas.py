from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class HomeTimelineRequestVariablesContract(BaseModel):
    count: Optional[int] = Field(20, alias='count')
    include_promoted_content: Optional[bool] = Field(True, alias='includePromotedContent')
    latest_control_available: Optional[bool] = Field(True, alias='latestControlAvailable')
    request_context: Optional[str] = Field('launch', alias='requestContext')
    with_community: Optional[bool] = Field(True, alias='withCommunity')
    seen_tweetIds: Optional[List[str]] = Field(["1707341324985286834", "1707565081750290910"], alias='seenTweetIds')


class HomeTimelineRequestFeaturesContract(BaseModel):
    responsive_web_graphql_exclude_directive_enabled: Optional[bool] = Field(True)
    verified_phone_label_enabled: Optional[bool] = Field(False)
    responsive_web_home_pinned_timelines_enabled: Optional[bool] = Field(False)
    creator_subscriptions_tweet_preview_api_enabled: Optional[bool] = Field(True)
    responsive_web_graphql_timeline_navigation_enabled: Optional[bool] = Field(True)
    responsive_web_graphql_skip_user_profile_image_extensions_enabled: Optional[bool] = Field(False)
    tweetypie_unmention_optimization_enabled: Optional[bool] = Field(True)
    responsive_web_edit_tweet_api_enabled: Optional[bool] = Field(True)
    graphql_is_translatable_rweb_tweet_is_translatable_enabled: Optional[bool] = Field(True)
    view_counts_everywhere_api_enabled: Optional[bool] = Field(True)
    longform_notetweets_consumption_enabled: Optional[bool] = Field(True)
    responsive_web_twitter_article_tweet_consumption_enabled: Optional[bool] = Field(False)
    tweet_awards_web_tipping_enabled: Optional[bool] = Field(False)
    freedom_of_speech_not_reach_fetch_enabled: Optional[bool] = Field(True)
    standardized_nudges_misinfo: Optional[bool] = Field(True)
    tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled: Optional[bool] = Field(True)
    longform_notetweets_rich_text_read_enabled: Optional[bool] = Field(True)
    longform_notetweets_inline_media_enabled: Optional[bool] = Field(True)
    responsive_web_media_download_video_enabled: Optional[bool] = Field(False)
    responsive_web_enhance_cards_enabled: Optional[bool] = Field(False)


class HomeTimelineRequest(BaseModel):
    variables: Optional[HomeTimelineRequestVariablesContract] = Field(HomeTimelineRequestVariablesContract())
    features: Optional[HomeTimelineRequestFeaturesContract] = Field(HomeTimelineRequestFeaturesContract())
    query_id: Optional[str] = Field('-8TWbLqVU1ROq-eeErVc2w', alias='queryId')


class DescriptionContract(BaseModel):
    urls: Optional[List[str]] = None


class UrlsContract(BaseModel):
    display_url: Optional[str] = None
    expanded_url: Optional[str] = None
    url: Optional[str] = None
    indices: Optional[List[int]] = None


class UrlContract(BaseModel):
    urls: Optional[List[UrlsContract]] = None


class EntitiesContract(BaseModel):
    description: Optional[DescriptionContract] = None
    url: Optional[UrlContract] = None


class TweetResultCoreUserResultsResultLegacyContract(BaseModel):
    typename: Optional[str] = Field(None, alias='__typename')
    following: Optional[bool] = None
    can_dm: Optional[bool] = None
    can_media_tag: Optional[bool] = None
    created_at: Optional[str] = None
    default_profile: Optional[bool] = None
    default_profile_image: Optional[bool] = None
    description: Optional[str] = None
    entries: Optional[EntitiesContract] = None
    fast_followers_count: Optional[int] = None
    favourites_count: Optional[int] = None
    followers_count: Optional[int] = None
    friends_count: Optional[int] = None
    has_custom_timelines: Optional[bool] = None
    is_translator: Optional[bool] = None
    listed_count: Optional[int] = None
    location: Optional[str] = None
    media_count: Optional[int] = None
    name: Optional[str] = None
    normal_followers_count: Optional[int] = None
    pinned_tweet_ids_str: Optional[List[str]] = None
    possibly_sensitive: Optional[bool] = None
    profile_banner_url: Optional[str] = None
    profile_image_url_https: Optional[str] = None
    profile_interstitial_type: Optional[str] = None
    screen_name: Optional[str] = None
    statuses_count: Optional[int] = None
    translator_type: Optional[str] = None
    url: Optional[str] = None
    verified: Optional[bool] = None
    verified_type: Optional[str] = None
    want_retweets: Optional[bool] = None
    withheld_in_countries: Optional[List[str]] = None


class TweetResultCoreUserResultsResultContract(BaseModel):
    typename: Optional[str] = Field(None, alias='__typename')
    id: Optional[str] = None
    rest_id: Optional[str] = None
    affiliates_highlighted_label: Optional[Dict[str, Any]] = None
    has_graduated_access: Optional[bool] = None
    is_blue_verified: Optional[bool] = None
    profile_image_shape: Optional[str] = None
    legacy: Optional[TweetResultCoreUserResultsResultLegacyContract] = None


class TweetResultCoreUserResultsContract(BaseModel):
    result: Optional[TweetResultCoreUserResultsResultContract] = None


class TweetResultCoreContract(BaseModel):
    user_results: Optional[TweetResultCoreUserResultsContract] = None


class UnifiedCardContract(BaseModel):
    card_fetch_state: Optional[str] = None


class EditControlContract(BaseModel):
    edit_tweet_ids: Optional[List[str]] = None
    editable_until_msecs: Optional[str] = None
    is_edit_eligible: Optional[bool] = None
    edits_remaining: Optional[str] = None


class ViewsContract(BaseModel):
    count: Optional[str] = None
    state: Optional[str] = None


class ExtMediaAvailabilityContract(BaseModel):
    status: Optional[str] = None


class FeaturesLargeContract(BaseModel):
    faces: Optional[List] = None


class FeaturesMediumContract(BaseModel):
    faces: Optional[List] = None


class FeaturesSmallContract(BaseModel):
    faces: Optional[List] = None


class FeaturesOrigContract(BaseModel):
    faces: Optional[List] = None


class FeaturesContract(BaseModel):
    large: Optional[FeaturesLargeContract] = None
    medium: Optional[FeaturesMediumContract] = None
    small: Optional[FeaturesSmallContract] = None
    orig: Optional[FeaturesOrigContract] = None


class SizesLargeContract(BaseModel):
    h: Optional[int] = None
    w: Optional[int] = None
    resize: Optional[str] = None


class SizesMediumContract(BaseModel):
    h: Optional[int] = None
    w: Optional[int] = None
    resize: Optional[str] = None


class SizesSmallContract(BaseModel):
    h: Optional[int] = None
    w: Optional[int] = None
    resize: Optional[str] = None


class SizesThumbContract(BaseModel):
    h: Optional[int] = None
    w: Optional[int] = None
    resize: Optional[str] = None


class SizesContract(BaseModel):
    large: Optional[SizesLargeContract] = None
    medium: Optional[SizesMediumContract] = None
    small: Optional[SizesSmallContract] = None
    thumb: Optional[SizesThumbContract] = None


class FocusRectContract(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None


class OriginalInfoContract(BaseModel):
    height: Optional[int] = None
    width: Optional[int] = None
    focus_rects: Optional[List[FocusRectContract]] = None


class MediaItemContract(BaseModel):
    display_url: Optional[str] = None
    expanded_url: Optional[str] = None
    id_str: Optional[str] = None
    indices: Optional[List[int]] = None
    media_key: Optional[str] = None
    media_url_https: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    ext_media_availability: Optional[ExtMediaAvailabilityContract] = None
    features: Optional[FeaturesContract] = None
    sizes: Optional[SizesContract] = None
    original_info: Optional[OriginalInfoContract] = None


class TweetResultLegacyEntitiesUrlsContract(BaseModel):
    display_url: Optional[str] = None
    expanded_url: Optional[str] = None
    url: Optional[str] = None
    indices: Optional[List[int]] = None


class TweetResultLegacyEntitiesContract(BaseModel):
    media: Optional[List[MediaItemContract]] = None
    user_mentions: Optional[List] = None
    urls: Optional[List[TweetResultLegacyEntitiesUrlsContract]] = None
    hashtags: Optional[List] = None
    symbols: Optional[List] = None


class ExtendedEntitiesContract(BaseModel):
    media: Optional[List[MediaItemContract]] = None


class BoundingBoxContract(BaseModel):
    coordinates: List[List[List[float]]] = None
    type: str = None


class PlaceContract(BaseModel):
    bounding_box: Optional[BoundingBoxContract] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    full_name: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    place_type: Optional[str] = None
    url: Optional[str] = None


class QuotedPermalink(BaseModel):
    url: Optional[str] = None
    expanded: Optional[str] = None
    display: Optional[str] = None


class TweetResultLegacyContract(BaseModel):
    bookmark_count: Optional[int] = None
    bookmarked: Optional[bool] = None
    created_at: Optional[str] = None
    conversation_id_str: Optional[str] = None
    display_text_range: Optional[List[int]] = None
    entities: Optional[TweetResultLegacyEntitiesContract] = None
    extended_entities: Optional[ExtendedEntitiesContract] = None
    favorite_count: Optional[int] = None
    favorited: Optional[bool] = None
    full_text: Optional[str] = None
    is_quote_status: Optional[bool] = None
    lang: Optional[str] = None
    place: Optional[PlaceContract] = None
    quoted_status_id_str: Optional[str] = None
    quoted_status_permalink: Optional[QuotedPermalink] = None
    possibly_sensitive: Optional[bool] = None
    possibly_sensitive_editable: Optional[bool] = None
    quote_count: Optional[int] = None
    reply_count: Optional[int] = None
    retweet_count: Optional[int] = None
    retweeted: Optional[bool] = None
    user_id_str: Optional[str] = None
    id_str: Optional[str] = None

    class Config:
        require_by_default = False


class TweetResultsResultContract(BaseModel):
    typename: Optional[str] = Field(None, alias='__typename')
    rest_id: Optional[str] = None
    core: Optional[TweetResultCoreContract] = None
    unified_card: Optional[UnifiedCardContract] = None
    edit_control: Optional[EditControlContract] = None
    is_translatable: Optional[bool] = None
    views: Optional[ViewsContract] = None
    source: Optional[str] = None
    legacy: Optional[TweetResultLegacyContract] = None


class TweetResultsContract(BaseModel):
    result: Optional[TweetResultsResultContract] = None


class ItemContentContract(BaseModel):
    item_type: Optional[str] = Field(None, alias='itemType')
    typename: Optional[str] = Field(None, alias='__typename')
    tweet_results: Optional[TweetResultsContract] = None
    tweet_display_type: Optional[str] = Field(None, alias='tweetDisplayType')


class FeedbackInfoContract(BaseModel):
    feedback_keys: Optional[List[str]] = Field(None, alias='feedbackKeys')


class TimelinesDetailsContract(BaseModel):
    injection_type: Optional[str] = Field(None, alias='injectionType')
    controller_data: Optional[str] = Field(None, alias='controllerData')


class DetailsContract(BaseModel):
    timelines_details: Optional[TimelinesDetailsContract] = Field(None, alias='timelinesDetails')


class ClientEventInfoContract(BaseModel):
    component: Optional[str] = None
    element: Optional[str] = None
    details: Optional[DetailsContract] = None


class ContentContract(BaseModel):
    entry_type: Optional[str] = None
    typename: Optional[str] = Field(None, alias='__typename')
    item_content: Optional[ItemContentContract] = Field(None, alias='itemContent')
    feedback_info: Optional[FeedbackInfoContract] = Field(None, alias='feedbackInfo')
    client_event_info: Optional[ClientEventInfoContract] = Field(None, alias='clientEventInfo')


class EntryContract(BaseModel):
    entry_id: Optional[str] = Field(None, alias='entryId')
    sort_index: Optional[str] = Field(None, alias='sortIndex')
    content: Optional[ContentContract] = None


class InstructionContract(BaseModel):
    type: Optional[str] = None
    entries: Optional[List[EntryContract]] = None


class ScribeConfigContract(BaseModel):
    page: Optional[str] = None


class MetadataContract(BaseModel):
    scribe_config: Optional[ScribeConfigContract] = Field(None, alias='scribeConfig')


class HomeTimelineUrtContract(BaseModel):
    instructions: Optional[List[InstructionContract]] = None
    response_objects: Optional[Any] = None
    metadata: Optional[MetadataContract] = None


class HomeContract(BaseModel):
    home_timeline_urt: Optional[HomeTimelineUrtContract] = None


class DataContract(BaseModel):
    home: Optional[HomeContract] = None


class HomeTimelineResponse(BaseModel):
    data: Optional[DataContract] = None
