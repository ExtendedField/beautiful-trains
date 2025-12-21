from functools import wraps
from typing import List

import networkx as nx
import numpy as np
from geopandas import GeoSeries
from shapely import MultiLineString, Point, STRtree
from momepy import gdf_to_nx
from networkx import relabel_nodes, Graph

from city_network.network import Network
from city_network.network_components import Connection, Node
from city_network.schemas import ConnectionMetaData
from city_network.config import TransitModeAndResistance


def graph_from_shapes(shapes: MultiLineString, relabel_mapping: dict = {}) -> Graph:
    graph = gdf_to_nx(GeoSeries(shapes).explode())
    graph = relabel_nodes(graph, relabel_mapping)
    return graph


def connect_network_graph(network: Network) -> None:
    _connect_graph_using_tree(network.graph, network.tree)


def connect_spacial_graph(g: Graph) -> None:
    tree = STRtree([Point(node.longitude, node.latitude) for node in g])
    _connect_graph_using_tree(g, tree)


def _connect_graph_using_tree(
    graph: Graph,
    tree: STRtree,
    min_dist: float = 0.005,
    max_dist: float = 1,
    increment: float = 0.005,
) -> None:
    if nx.is_connected(graph):
        return
    else:
        node_list = np.array(list(graph.nodes()))
        largest_subgraph = max(nx.connected_components(graph), key=len)
        disconnected_subgraphs = [
            graph.subgraph(subgraph)
            for subgraph in nx.connected_components(graph)
            if len(subgraph) < len(largest_subgraph)
        ]
        target = disconnected_subgraphs[0]
        nodes_in_largest_subgraph = list(target.nodes())
        starting = nodes_in_largest_subgraph[0]
        valid_targs = []
        while (min_dist < max_dist) & (len(valid_targs) < 1):
            valid_targs += [
                node
                for node in node_list[
                    tree.query(
                        starting.location, predicate="dwithin", distance=min_dist
                    )
                ]
                if node not in nodes_in_largest_subgraph
            ]
            min_dist += increment
        ending = valid_targs[0]
        connection_meta_data = ConnectionMetaData(
            station1=starting,
            station2=ending,
            transit_modes_and_resistances=[TransitModeAndResistance("street")],
        )
        u, v, connection_data = Connection(connection_meta_data).get_weighted_tuple()
        graph.add_edge(u, v, **connection_data)
        _connect_graph_using_tree(graph, tree)
