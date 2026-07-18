from city_network.network_components import Node
from city_network.config import TransitMode
from shapely import Point, STRtree
import networkx as nx
import numpy as np

# TODO: very slow


def connect_spacial_graph(graph: nx.MultiDiGraph) -> None:
    tree = STRtree([Point(data["x"], data["y"]) for _, data in graph.nodes(data=True)])
    _trim_small_subgraphs(graph)
    connect_graph_using_tree(graph, tree)


def connect_graph_using_tree(
    graph: nx.MultiDiGraph,
    tree: STRtree,
    min_dist: float = 0.005,
    max_dist: float = 1,
    increment: float = 0.005,
) -> None:
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
        print(
            f"Found {len(disconnected_subgraphs)} meaningful subgraphs which are not strongly connected."
        )
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
        _connect_subgraphs(graph, starting_node, ending_node)
        connect_graph_using_tree(graph, tree)


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


def _connect_subgraphs(
    graph: nx.MultiDiGraph, starting_node: Node, ending_node: Node
) -> None:
    # Both edges are needed as in general this will be a multi-di graph
    graph.add_edge(
        starting_node.network_id,
        ending_node.network_id,
        edge_weight=TransitMode.WALK.resistance()
        * euclidean_distance(starting_node.location, ending_node.location),
    )
    graph.add_edge(
        ending_node.network_id,
        starting_node.network_id,
        edge_weight=TransitMode.WALK.resistance()
        * euclidean_distance(starting_node.location, ending_node.location),
    )


def euclidean_distance(point1: Point, point2: Point):
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5
