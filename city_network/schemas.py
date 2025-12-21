from typing import List, Set
from enum import Enum

from pydantic import BaseModel
from shapely import Point

from city_network.network_components import Connection, Node


class ModeResistancePair(BaseModel):
    mode: str
    resistance: float


class TransitModeAndResistance(Enum):
    WALK = ModeResistancePair(mode="walk", resistance=1)
    BUS = ModeResistancePair(mode="bus", resistance=0.5)
    STREETCAR = ModeResistancePair(mode="streetcar", resistance=0.5)
    LIGHT_RAIL = ModeResistancePair(mode="light_rail", resistance=0.3)
    HEAVY_RAIL = ModeResistancePair(mode="heavy_rail", resistance=0.2)


class LineColorPair(BaseModel):
    name: str
    color: str = "black"  # TODO: this should be some color datatype


class LineMetaData(BaseModel):
    stations: Set[Node]
    connections: Set[Connection]
    name_and_color: LineColorPair
    line_type_and_resistance: TransitModeAndResistance
    weight: float


class NodeMetaData(BaseModel):
    net_id: str
    name: str
    location: Point
    available_lines: List[LineColorPair] = []
    transit_modes_and_resistances: List[TransitModeAndResistance]


class ConnectionMetaData(BaseModel):
    station1: Node
    station2: Node
    transit_modes_and_resistances: List[TransitModeAndResistance]
