from city_network.network_components import Connection
import networkx as nx
from shapely import Point, STRtree
from tqdm import tqdm

from city_network.config import TransitMode
from city_network.network_components import Node


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
        largest_subgraph_length = len(
            max(nx.strongly_connected_components(graph), key=len)
        )
        disconnected_subgraphs = [
            graph.subgraph(subgraph)
            for subgraph in nx.strongly_connected_components(graph)
            if len(subgraph) < largest_subgraph_length
        ]
        nodes_in_disconnected_subgraph = _node_list_from_graph(
            disconnected_subgraphs[0]
        )
        starting_node = nodes_in_disconnected_subgraph[0]
        valid_targs: list[Node] = []
        while (min_dist < max_dist) & (len(valid_targs) < 1):
            nearby_nodes_indexes = tree.query(
                starting_node.location,
                predicate="dwithin",
                distance=min_dist,
            )  # np.array of int
            nearby_nodes = [node_list[int(i)] for i in nearby_nodes_indexes]
            valid_targs += [
                node
                for node in nearby_nodes
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
    return graph


def euclidean_distance(point1: Point, point2: Point):
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5


def get_potential_new_connections(graph: nx.MultiDiGraph) -> list[Connection]:
    # TODO: this whole function is insanely heavy.
    #       The graph simply needs to be more conservative. custom leaner query
    #       Also, graph compliment -> search all connections is no sclabale at all
    graph_compliment = nx.Graph(nx.complement(nx.DiGraph(graph)))
    original_nodes_with_date = graph.nodes(data=True)
    return [
        Connection(
            Node(
                network_id=starting_id,
                location=Point(
                    original_nodes_with_date[starting_id]["x"],
                    original_nodes_with_date[starting_id]["y"],
                ),
            ),
            Node(
                network_id=ending_id,
                location=Point(
                    original_nodes_with_date[ending_id]["x"],
                    original_nodes_with_date[ending_id]["y"],
                ),
            ),
        )
        for starting_id, ending_id in graph_compliment.edges()
    ]
