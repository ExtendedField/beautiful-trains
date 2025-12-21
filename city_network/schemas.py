from typing import List, Set

from pydantic import BaseModel
from shapely import MultiLineString, Point

from city_network.config import TransitModeAndResistance
from city_network.network_components import Connection, Node, Line


class ModeResistancePair(BaseModel):
    mode: str
    resistance: float


class LineColorPair(BaseModel):
    name: str
    color: str = "black"  # TODO: this should be some color datatype


class TransitShapes(BaseModel):
    line_and_color = LineColorPair
    shape = MultiLineString


class ComponentMetaData(BaseModel):
    pass


class LineMetaData(ComponentMetaData):
    stations: Set[Node]
    connections: Set[Connection]
    name_and_color: LineColorPair
    line_type_and_resistance: TransitModeAndResistance
    weight: float


class NodeMetaData(ComponentMetaData):
    net_id: str
    name: str = ""
    location: Point
    available_lines: List[LineColorPair] = []
    transit_modes_and_resistances: List[TransitModeAndResistance] = []


class ConnectionMetaData(ComponentMetaData):
    station1: Node
    station2: Node
    transit_modes_and_resistances: List[TransitModeAndResistance]


class NetworkMetaData(ComponentMetaData):
    city: str
    lines: List[Line]
    transit_shapes: List[TransitShapes]
    walking_shapes: MultiLineString
