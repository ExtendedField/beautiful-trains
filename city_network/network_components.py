from typing import List, Tuple

from networkx import Graph
from numpy import cos, sqrt

from city_network.schemas import (
    NodeMetaData,
    LineMetaData,
    ConnectionMetaData,
)
from city_network.config import TransitModeAndResistance


class Line:
    def __init__(self, line_meta_data: LineMetaData):
        self.stations = line_meta_data.stations
        self.connections = line_meta_data.connections

        line_mode_and_resistance = line_meta_data.line_type_and_resistance.value
        self.line_type = line_mode_and_resistance.mode
        self.resistance = line_mode_and_resistance.resistance

        self.name = line_meta_data.name_and_color

        line_graph = Graph()
        line_graph.add_nodes_from(line_meta_data.stations)
        line_graph.add_edges_from(
            [
                connection.get_weighted_tuple()
                for connection in line_meta_data.connections
            ]
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


class Node:
    def __init__(self, node_meta_data: NodeMetaData):
        available_transit_modes = [
            mode_and_resistance.value.mode
            for mode_and_resistance in node_meta_data.transit_modes_and_resistances
        ]
        self.available_transit_modes = available_transit_modes
        self.available_lines = node_meta_data.available_lines
        self.network_id = node_meta_data.net_id
        self.name = node_meta_data.name
        self.location = node_meta_data.location

    def __str__(self) -> str:
        line_names = [line.name for line in self.available_lines]
        return f"{self.name}: {", ".join(line_names)}"

    def lat(self) -> float:
        return self.location.y

    def long(self) -> float:
        return self.location.x


class Connection:
    def __init__(self, connection_meta_data: ConnectionMetaData):
        self.station1 = connection_meta_data.station1
        self.station2 = connection_meta_data.station2
        self.conn_types_and_resistances = (
            connection_meta_data.transit_modes_and_resistances
        )
        long1 = self.station1.long()
        long2 = self.station2.long()
        lat1 = self.station1.lat()
        lat2 = self.station2.lat()
        deglen = 110.25  # fixed lengths of a degree of latitude on earth

        x_dist = long1 - long2
        y_dist = (lat1 - lat2) * cos(long2)
        # Euclidean distance.
        self.travel_resistance = (
            deglen
            * sqrt(x_dist**2 + y_dist**2)
            * _get_resistance(self.conn_types_and_resistances)  # kms
        )

    def __str__(self) -> str:
        return f"{self.station1.name}<->{self.station2.name}"

    def get_unweighted_tuple(self) -> Tuple[Node, Node]:
        return self.station1, self.station2

    def get_weighted_tuple(self) -> Tuple[Node, Node, dict]:
        # Matches format expected by NetworkX for weighted conncetions
        available_transit_modes = self.conn_types_and_resistances
        return (
            self.station1,
            self.station2,
            {
                "travel_resistance": self.travel_resistance,
                "available_transit_modes": available_transit_modes,
                "lines": set(
                    self.station1.available_lines + self.station2.available_lines
                ),
            },
        )


def _get_resistance(types_and_resistances: List[TransitModeAndResistance]) -> float:
    resistance = min(
        [
            mode_and_resistance.value.resistance
            for mode_and_resistance in types_and_resistances
        ]
    )
    return resistance
