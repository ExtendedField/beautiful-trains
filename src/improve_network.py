from networkx import MultiDiGraph
import networkx as nx
from copy import deepcopy


def find_n_best_new_connections(
    transit_network: MultiDiGraph, n: int = 1
) -> MultiDiGraph:
    if (n < 1) | (nx.is_connected(transit_network)):
        return transit_network
    optimized_transit_network = deepcopy(transit_network)
    optimized_transit_network = _find_best_new_connection(
        transit_network=optimized_transit_network
    )
    n = n - 1
    return find_n_best_new_connections(optimized_transit_network, n)


def _find_best_new_connection(transit_network: MultiDiGraph) -> MultiDiGraph:
    potential_new_connections = nx.Graph(nx.complement(transit_network)).edges()
    current_best_mean_shortest_path_length = nx.average_shortest_path_length(
        transit_network
    )
    optimized_graph = transit_network
    for new_connection in potential_new_connections:
        candidate_graph = transit_network.add_edge(  # pyrefly: ignore TODO: I think this works but should make typechecker happy
            new_connection
        )
        mean_shortest_path_length = nx.average_shortest_path_length(candidate_graph)
        if mean_shortest_path_length < current_best_mean_shortest_path_length:
            current_best_mean_shortest_path_length = mean_shortest_path_length
            optimized_graph = candidate_graph
    return optimized_graph
