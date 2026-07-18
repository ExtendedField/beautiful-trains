from uuid import UUID
from typing import Any
from networkx import Graph
from numpy import cos, sqrt
from shapely import Point

from city_network.config import TransitMode
from city_network.schemas import LineColorPair

# Connection and Node can both be pydantic schemas with helper funcs I think


class Node:
    def __init__(
        self,
        net_id: UUID,
        location: Point,
        transit_modes: set[TransitMode] = set(),
        available_lines: list[LineColorPair] = [],
        name: str = "",
    ):
        self.available_transit_modes = {TransitMode.WALK}.union(transit_modes)
        self.available_lines = available_lines
        self.network_id = net_id
        self.name = name
        self.location = location

    def __str__(self) -> str:
        line_names = [line.name for line in self.available_lines]
        return f"{self.name}: {', '.join(line_names)}"

    def lat(self) -> float:
        return self.location.y

    def long(self) -> float:
        return self.location.x


class Connection:
    def __init__(self, station1: Node, station2: Node, transit_modes: list[TransitMode]):
        self.station1 = station1
        self.station2 = station2
        self.conn_types = transit_modes
        long1 = self.station1.long()
        long2 = self.station2.long()
        lat1 = self.station1.lat()
        lat2 = self.station2.lat()
        deglen = 110.25  # fixed lengths of a degree of latitude on earth (kms)

        x_dist = long1 - long2
        y_dist = (lat1 - lat2) * cos(long2)
        # Euclidean distance.
        self.travel_resistance = float(
            deglen * sqrt(x_dist**2 + y_dist**2) * _get_resistance(self.conn_types)  # kms
        )

    def __str__(self) -> str:
        return f"{self.station1.name}<->{self.station2.name}"

    def get_unweighted_tuple(self) -> tuple[Node, Node]:
        return self.station1, self.station2

    def get_weighted_tuple(self) -> tuple[Node, Node, dict[str, Any]]:
        # Matches format expected by NetworkX for weighted connections
        available_transit_modes = self.conn_types
        return (
            self.station1,
            self.station2,
            {
                "travel_resistance": self.travel_resistance,
                "available_transit_modes": available_transit_modes,
                "lines": set(self.station1.available_lines + self.station2.available_lines),
            },
        )


def _get_resistance(transit_modes: list[TransitMode]) -> float:
    resistance = min([transit_mode.resistance() for transit_mode in transit_modes])
    return resistance


class Line:
    def __init__(
        self,
        stations: set[Node],
        connections: set[Connection],
        line_type: TransitMode,
        name_and_color: LineColorPair,
    ):
        self.stations = stations
        self.connections = connections

        self.line_type = line_type
        self.resistance = line_type.resistance()

        self.name = name_and_color

        line_graph = Graph()
        line_graph.add_nodes_from(stations)
        line_graph.add_edges_from(
            [connection.get_weighted_tuple() for connection in connections]
        )
        self._remove_inactive_stations(line_graph)
        self.line_graph = line_graph

    def _remove_inactive_stations(self, graph: Graph) -> None:
        active_stations = [connection.station1 for connection in self.connections] + [
            connection.station2 for connection in self.connections
        ]
        graph.remove_nodes_from(
            [station for station in self.stations if station not in active_stations]
        )

    def __str__(self):
        return f"{self.name} line. number of stations:{len(self.stations)}"
