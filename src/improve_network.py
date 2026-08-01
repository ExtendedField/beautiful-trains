from copy import deepcopy

import networkx as nx
from networkx import MultiDiGraph
from tqdm import tqdm

from utils import add_two_way_edge


def find_n_best_new_connections(transit_network: MultiDiGraph, n: int = 1) -> MultiDiGraph:
    # TODO: progress bar here as well
    if n < 1:
        print("All connections found.")
        return transit_network
    optimized_transit_network = deepcopy(transit_network)
    optimized_transit_network = _find_best_new_connection(
        transit_network=optimized_transit_network
    )
    n = n - 1
    print(f"New connection found. {n} more to go!")
    return find_n_best_new_connections(optimized_transit_network, n)


def _find_best_new_connection(transit_network: MultiDiGraph) -> MultiDiGraph:
    potential_new_connections = nx.Graph(
        nx.complement(transit_network)  # TODO: why does this take forever?
    ).edges()
    current_best_mean_shortest_path_length = nx.average_shortest_path_length(
        transit_network
    )
    # TODO: this whole thing is slow because we are using a multidigraph.
    # The way to make this faster is to do the optimizations with a flat undirected graph
    optimized_graph = deepcopy(transit_network)
    for new_connection in tqdm(
        potential_new_connections, desc="Testing possible connections"
    ):
        candidate_graph = add_two_way_edge(transit_network, *new_connection)
        candidate_mean_shortest_path_length = nx.average_shortest_path_length(
            candidate_graph
        )
        if candidate_mean_shortest_path_length < current_best_mean_shortest_path_length:
            current_best_mean_shortest_path_length = candidate_mean_shortest_path_length
            optimized_graph = candidate_graph
    return optimized_graph
