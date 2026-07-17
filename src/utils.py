from city_network.config import TransitMode
from shapely import Point, STRtree
import networkx as nx
import numpy as np


def connect_spacial_graph(g: nx.MultiDiGraph) -> None:
    tree = STRtree([Point(node.longitude, node.latitude) for node in g])
    connect_graph_using_tree(g, tree)


def connect_graph_using_tree(
    graph: nx.MultiDiGraph,
    tree: STRtree,
    min_dist: float = 0.005,
    max_dist: float = 1,
    increment: float = 0.005,
) -> None:
    if nx.is_connected(graph):
        return
    else:
        node_list = np.array(list(graph.nodes()))
        largest_subgraph = max(nx.strongly_connected_components(graph), key=len)
        disconnected_subgraphs = [
            graph.subgraph(subgraph)
            for subgraph in nx.strongly_connected_components(graph)
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
        distance = _euclidean_distance(starting, ending)
        graph.add_edge(
            starting, ending, edge_weight=TransitMode.WALK.resistance() * distance
        )
        connect_graph_using_tree(graph, tree)


def _euclidean_distance(node1, node2):
    return (
        (node1.longitude - node2.longitude) ** 2
        + (node1.latitude - node2.latitude) ** 2
    ) ** 0.5
