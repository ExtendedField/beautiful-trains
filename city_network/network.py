from tqdm import tqdm
import networkx as nx
import numpy as np
from numpy.typing import NDArray

from typing import List, Set
from shapely import Point, STRtree

from city_network.network_components import Connection, Node
from city_network.utils import graph_from_shapes, connect_network_graph
from city_network.config import TransitModeAndResistance
from city_network.schemas import ConnectionMetaData, NetworkMetaData, NodeMetaData


class Network:
    def __init__(self, network_meta_data: NetworkMetaData):
        self.city = network_meta_data.city
        self.lines = network_meta_data.lines
        self.transit_shapes = network_meta_data.transit_shapes
        self.walking_shapes = network_meta_data.walking_shapes
        unpacked_connections = [line.connections for line in self.lines]
        self.transit_connections = {
            connections
            for connections_set in unpacked_connections
            for connections in connections_set
        }
        available_modes: Set[str] = set()
        transit_nodes: List[Set[Node]] = list()
        for line in self.lines:
            available_modes.add(line.line_type)
            transit_nodes.append(line.stations)

        self.available_modes = available_modes
        self.transit_nodes: Set[Node] = set().union(*transit_nodes)

        self.walking_graph = self._build_walking_graph()
        self.transit_graph = self._build_transit_graph()
        self.graph = self._combine_graph_layers()

        self.walking_nodes = self._get_walking_nodes()
        self.nodes = self.walking_nodes.union(self.transit_nodes)

        self.walking_connections = self._get_transit_nodes()
        self.connections = self.transit_connections.union(self.walking_connections)

    def __str__(self):
        return f"{self.city}'s transit network. Number of rail lines: {len(self.lines)}\nTotal nodes: {len(self.nodes)}"

    def _build_walking_graph(self) -> nx.Graph:
        relabel_mapping = dict()
        walking_graph = graph_from_shapes(self.walking_shapes, relabel_mapping)
        dists = nx.get_edge_attributes(walking_graph, name="mm_len")
        for edge_key in dists.keys():
            # mm -> km * resistance factor for walking
            dists[edge_key] = (
                float(dists[edge_key])
                * 1000
                * TransitModeAndResistance("walk").value.resistance
            )
        nx.set_edge_attributes(walking_graph, values=dists, name="travel_resistance")
        return walking_graph

    def _build_transit_graph(self) -> nx.Graph:
        line_graphs = {line.line_graph for line in self.lines}
        return nx.compose_all(line_graphs)

    def _combine_graph_layers(self, threshold: float = 0.0008) -> nx.Graph:
        node_list = np.array(list(self.nodes))
        self.tree = STRtree([node.location for node in node_list])
        layer_connections: Set[Connection] = set()
        for node1 in tqdm(self.walking_graph, desc="Stitching together graph layers"):
            neighborhood = node_list.take(
                self.tree.query(node1.location, predicate="dwithin", distance=threshold)
            ).tolist()
            neighborhood = [node for node in neighborhood if node.node_type != "street"]
            new_connections = {
                Connection(
                    ConnectionMetaData(
                        station1=node1,
                        station2=node2,
                        transit_modes_and_resistances=[
                            TransitModeAndResistance("walk")
                        ],
                    )
                )
                for node2 in neighborhood
            }
            layer_connections = layer_connections.union(new_connections)
        connected_graph = nx.from_edgelist(
            [connection.get_weighted_tuple() for connection in layer_connections]
        )
        connect_network_graph(self)
        return connected_graph

    def _get_walking_nodes(self) -> Set[Node]:
        return {
            Node(
                NodeMetaData(
                    net_id="",  # TODO: generate unique node_id in a better way.
                    location=Point(data["latitude"], data["longitude"]),
                )
            )
            for node, data in self.graph.nodes
        }

    def _get_transit_nodes(self) -> Set[Connection]:
        return {
            Connection(
                ConnectionMetaData(
                    station1=node1,
                    station2=node2,
                    transit_modes_and_resistances=[TransitModeAndResistance["walk"]],
                )
            )
            for node1, node2 in self.graph.edges
        }
