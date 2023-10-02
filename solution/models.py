import uuid
from typing import Literal, Dict, Any, List, Optional

from pydantic import BaseModel, Field


class MediaItemModel(BaseModel):
    id: str = Field()
    type: Literal['image', 'audio', 'video']
    title: str = Field()
    file_name: str = Field()
    url: str = Field()


class MessageModel(BaseModel):
    id: str = Field()  # required
    text: str = Field()  # required
    language: Optional[str] = None
    enrichment: Optional[str] = None
    media: List[MediaItemModel] = Field()


class UserModel(BaseModel):
    id: str = Field()
    name: str = Field()


class ChannelModel(BaseModel):
    id: str = Field()
    name: str = Field()


class ReferencedPostModel(BaseModel):
    id: str = Field()
    url: str = Field()


class Point(BaseModel):
    bbox: List[float] = None
    coordinates: List[float] = None
    type: str = None


class LineString(BaseModel):
    bbox: List[float] = None
    coordinates: List[List[float]] = None
    type: str = None


class Polygon(BaseModel):
    bbox: List[float] = None
    coordinates: List[List[List[float]]] = None
    type: str = None


class MultiPoint(BaseModel):
    bbox: List[float] = None
    coordinates: List[List[float]] = None
    type: str = None


class MultiLineString(BaseModel):
    bbox: List[float] = None
    coordinates: List[List[List[float]]] = None
    type: str = None


class MultiPolygon(BaseModel):
    bbox: List[float] = None
    coordinates: List[List[List[List[float]]]] = None
    type: str = None


class GeometryCollection(BaseModel):
    bbox: List[float] = None
    geometries: List[Point | LineString | Polygon | MultiPoint | MultiLineString | MultiPolygon] = None
    type: str = None


class Feature(BaseModel):
    bbox: List[float] = None
    geometry: Point | LineString | Polygon | MultiPoint | MultiLineString | MultiPolygon | GeometryCollection = None
    id: float | str = None
    properties: Optional[Any] = None
    type: str = None


class FeatureCollection(BaseModel):
    bbox: List[float] = None
    features: List[Feature]


class SourceModel(BaseModel):
    platform: str = Field()
    channel: ChannelModel = Field()
    referenced_post: Optional[ReferencedPostModel] = None
    source_specific_fields: Optional[Dict[str, str]] = None


class TweetModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias='_id')
    timestamp: int = Field()
    message: MessageModel = Field()
    user: UserModel = Field()
    geo_coords: Optional[
        Point | \
        LineString | \
        Polygon | MultiPoint | \
        MultiLineString | \
        MultiPolygon | \
        GeometryCollection | \
        Feature | \
        FeatureCollection
        ] = None  # not required
    source: SourceModel = Field()
