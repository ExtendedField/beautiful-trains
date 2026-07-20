from copy import deepcopy
from tqdm import tqdm
from city_network.network_components import Node
from city_network.config import TransitMode
from shapely import Point, STRtree
import networkx as nx
import numpy as np


def connect_spacial_graph(graph: nx.MultiDiGraph) -> None:
    tree = STRtree([Point(data["x"], data["y"]) for _, data in graph.nodes(data=True)])
    _trim_small_subgraphs(graph)
    progress_bar = tqdm(
        total=len(list(nx.strongly_connected_components(graph))),
        desc="Connecting disconnected subgraphs",
    )
    connect_graph_using_tree(graph, tree, progress_bar)


# TODO: write a test for this because it keeps breaking
def connect_graph_using_tree(
    graph: nx.MultiDiGraph,
    tree: STRtree,
    progress_bar: tqdm,
    min_dist: float = 0.005,
    max_dist: float = 1,
    increment: float = 0.005,
) -> None:
    progress_bar.update(1)
    if nx.is_strongly_connected(graph):
        return
    else:
        node_list = _node_list_from_graph(graph)
        largest_subgraph_length = len(max(nx.strongly_connected_components(graph), key=len))
        disconnected_subgraphs = [
            graph.subgraph(subgraph)
            for subgraph in nx.strongly_connected_components(graph)
            if len(subgraph) < largest_subgraph_length
        ]
        nodes_in_disconnected_subgraph = _node_list_from_graph(disconnected_subgraphs[0])
        starting_node = nodes_in_disconnected_subgraph[0]
        valid_targs = []
        while (min_dist < max_dist) & (len(valid_targs) < 1):
            valid_targs += [
                node
                for node in np.array(node_list)[
                    tree.query(
                        starting_node.location,
                        predicate="dwithin",
                        distance=min_dist,
                    )
                ]
                if node not in nodes_in_disconnected_subgraph
            ]
            min_dist += increment
        ending_node = valid_targs[0]
        graph = add_two_way_edge(graph, starting_node, ending_node)
        connect_graph_using_tree(graph, tree, progress_bar)


def _trim_small_subgraphs(graph: nx.MultiDiGraph) -> None:
    for component in list(nx.strongly_connected_components(graph)):
        if len(component) <= 3:
            for node in component:
                graph.remove_node(node)


def _node_list_from_graph(graph: nx.MultiDiGraph) -> list[Node]:
    return [
        Node(network_id=node, location=Point(data["x"], data["y"]))
        for node, data in graph.nodes(data=True)
    ]


def add_two_way_edge(
    graph: nx.MultiDiGraph, starting_node: Node, ending_node: Node
) -> nx.MultiDiGraph:
    # Both edges are needed as in general this will be a multi-di graph
    # TODO: ifs here -> function is overloaded becuase we dont use Node everywhere
    graph.add_edge(
        starting_node.network_id if starting_node.network_id else starting_node,
        ending_node.network_id if ending_node.network_id else ending_node,
        edge_weight=TransitMode.WALK.resistance()
        * euclidean_distance(starting_node.location, ending_node.location),
    )
    graph.add_edge(
        ending_node.network_id if ending_node.network_id else ending_node,
        starting_node.network_id if starting_node.network_id else starting_node,
        edge_weight=TransitMode.WALK.resistance()
        * euclidean_distance(starting_node.location, ending_node.location),
    )
    return graph


def euclidean_distance(point1: Point, point2: Point):
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5
