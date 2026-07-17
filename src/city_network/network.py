from networkx import MultiDiGraph
from tqdm import tqdm
import networkx as nx
import numpy as np
from uuid import uuid4

from typing import List, Set
from shapely import MultiLineString, Point, STRtree

from city_network.network_components import Connection, Line, Node
from city_network.utils import graph_from_shapes, connect_graph_using_tree
from city_network.config import TransitMode
from city_network.schema import TransitShape


class Network:
    def __init__(
        self, public_transit_network: MultiDiGraph, walking_network: MultiDiGraph
    ):
        # TODO: think abut either fleshing this out to make osmnx compatible
        #       or thing about building a network as an intermediate step if
        #       that makes more sense.
        self.walking_graph = walking_network
        self.transit_graph = public_transit_network

    def __init__(
        self,
        city: str,
        lines: List[Line],
        transit_shapes: List[TransitShape],
        walking_shapes: MultiLineString,
    ):
        self.city = city
        self.lines = lines
        self.transit_shapes = transit_shapes
        self.walking_shapes = walking_shapes
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

        self.walking_nodes = self._get_walking_nodes()
        self.nodes = self.walking_nodes.union(self.transit_nodes)
        self.graph = self._combine_graph_layers()

        self.walking_connections = self._get_transit_nodes()
        self.connections = self.transit_connections.union(self.walking_connections)

    def __str__(self):
        return f"{self.city}'s transit network. Number of rail lines: {len(self.lines)}\nTotal nodes: {len(self.nodes)}"

    def _build_walking_graph(self) -> nx.Graph:
        relabel_mapping = dict()
        walking_graph = graph_from_shapes(self.walking_shapes, relabel_mapping)
        dists = nx.get_edge_attributes(walking_graph, name="mm_len")  # pyrefly: ignore
        for edge_key in dists.keys():
            # mm -> km * resistance factor for walking
            dists[edge_key] = (
                float(dists[edge_key]) * 1000 * TransitMode.WALK.resistance()
            )
        nx.set_edge_attributes(  # pyrefly: ignore
            walking_graph, values=dists, name="travel_resistance"
        )
        return walking_graph

    def _build_transit_graph(self) -> nx.Graph:
        line_graphs = {line.line_graph for line in self.lines}
        return nx.compose_all(line_graphs)  # pyrefly: ignore

    def _combine_graph_layers(self, threshold: float = 0.0008) -> nx.Graph:
        node_list = np.array(list(self.nodes))
        self.tree = STRtree([node.location for node in node_list])
        layer_connections: Set[Connection] = set()
        for node1 in tqdm(self.transit_nodes, desc="Stitching together graph layers"):
            neighborhood = node_list.take(
                self.tree.query(node1.location, predicate="dwithin", distance=threshold)
            ).tolist()
            walking_only_nodes_in_neighborhood = [
                node
                for node in neighborhood
                if node.available_transit_modes == [TransitMode.WALK]
            ]
            new_connections = {
                Connection(
                    station1=node1,
                    station2=node2,
                    transit_modes=[TransitMode.WALK],
                )
                for node2 in walking_only_nodes_in_neighborhood
            }
            layer_connections = layer_connections.union(new_connections)
        new_connections = nx.MultiGraph(
            [connection.get_weighted_tuple() for connection in layer_connections]
        )
        combined_graphs = nx.Graph(
            nx.compose_all(  # pyrefly: ignore
                [
                    nx.MultiGraph(self.walking_graph),
                    nx.MultiGraph(self.transit_graph),
                    new_connections,
                ]
            )
        )
        connected_graph = connect_graph_using_tree(combined_graphs, self.tree)
        if connected_graph:
            return connected_graph
        else:
            exception_msg = (
                f"Graph could not be fully connected\n"
                f"walking nodes: {self.walking_nodes}\n"
                f"transit_nodes: {self.transit_nodes}"
            )
            raise Exception(exception_msg)

    def _get_walking_nodes(self) -> Set[Node]:
        return {
            Node(
                net_id=uuid4(),
                location=Point(lat, lon),
            )
            for lat, lon in self.walking_graph.nodes
        }

    def _get_transit_nodes(self) -> Set[Connection]:
        return {
            Connection(
                station1=node1,
                station2=node2,
                transit_modes=[TransitMode.WALK],
            )
            for node1, node2 in self.graph.edges
        }
