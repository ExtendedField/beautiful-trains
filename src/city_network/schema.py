from math import sqrt, cos

from city_network.config import TransitMode
from config.constants import KM_PER_DEG_LATITUDE_EARTH

from pydantic import BaseModel, ConfigDict
from networkx import Graph
from shapely import Point, MultiLineString
from uuid import UUID


class LineColorPair(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    color: str = "black"  # TODO: this should be some color datatype.. or Enum!


class TransitShape(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    line_and_color: LineColorPair
    shape: MultiLineString


class Node(BaseModel):
    net_id: UUID
    name: str
    location: Point
    transit_modes: set[TransitMode] = {TransitMode.WALK}
    available_lines: list[LineColorPair] = []

    # TODO: verify this is the correct def for pydantic model helper funcs
    def __str__(self) -> str:
        line_names = [line.name for line in self.available_lines]
        return f"{self.name}: {', '.join(line_names)}"

    def lat(self) -> float:
        return self.location.y

    def long(self) -> float:
        return self.location.x


class Connection(BaseModel):
    node1: Node
    node2: Node
    transit_modes: set[TransitMode] = {TransitMode.WALK}

    def __str__(self) -> str:
        return f"{self.node1.name}<->{self.node2.name}"

    def get_networkx_connection_construcctor(self):
        return (
            self.node1,
            self.node2,
            {
                "travel_resistance": self.travel_resistance(),
                "available_transit_modes": self.transit_modes,
                "lines": set(self.node1.available_lines + self.node2.available_lines),
            },
        )

    def travel_resistance(self) -> float:
        min_resistance = min(
            [transit_mode.resistance() for transit_mode in self.transit_modes]
        )
        long1 = self.node1.long()
        long2 = self.node2.long()
        lat1 = self.node1.lat()
        lat2 = self.node2.lat()
        x_dist = long1 - long2
        y_dist = (lat1 - lat2) * cos(long2)
        return float(
            KM_PER_DEG_LATITUDE_EARTH * sqrt(x_dist**2 + y_dist**2) * min_resistance
        )


class Line(BaseModel):
    stations: set[Node]
    connections: set[Connection]
    line_type: TransitMode
    name_and_color: LineColorPair

    def line_graph(self) -> Graph:
        line_graph = Graph()
        line_graph.add_nodes_from(self.stations)
        line_graph.add_edges_from(
            [
                connection.get_networkx_connection_construcctor()
                for connection in self.connections
            ]
        )
        return line_graph

    def __str__(self):
        return (
            f"{self.name_and_color.name} line. number of stations:{len(self.stations)}"
        )
